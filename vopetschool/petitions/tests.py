import pytest
from datetime import timedelta
from django.urls import reverse
from django.utils import timezone
from django.test import Client
from django.contrib.auth import get_user_model
from petitions.models import Petition, Comment
from accounts.models import ClassGroup, Student

User = get_user_model()

@pytest.fixture
def client():
    return Client()

@pytest.fixture
def class_group(db):
    return ClassGroup.objects.create(name="11-Б")

@pytest.fixture
def student(db, class_group):
    user = User.objects.create_user(email="student@example.com", password="testpass123", role="student")
    student_profile = Student.objects.create(user=user)  # не передаємо school_class
    student_profile.school_class = class_group.name      # встановлюємо вручну
    student_profile.save()
    class_group.students.add(student_profile)
    return user


@pytest.fixture
def director(db):
    return User.objects.create_user(email="director@example.com", password="testpass123", role="director")

@pytest.fixture
def authenticated_student(client, student):
    client.login(email="student@example.com", password="testpass123")
    return client

@pytest.fixture
def authenticated_director(client, director):
    client.login(email="director@example.com", password="testpass123")
    return client

@pytest.fixture
def petition(student, class_group):
    return Petition.objects.create(
        title="Потрібен новий Wi-Fi",
        text="У школі поганий Wi-Fi, давайте змінювати!",
        deadline=timezone.now() + timedelta(days=3),
        level=Petition.Level.CLASS,
        status=Petition.Status.NEW,
        creator=student,
        class_group=class_group
    )


# --- Основні тести для Petition ---
@pytest.mark.django_db
def test_petition_list_view(authenticated_student):
    response = authenticated_student.get(reverse("petition_list"))
    assert response.status_code == 200
    assert "petitions" in response.context

@pytest.mark.django_db
def test_petition_create(authenticated_student, class_group):
    response = authenticated_student.post(reverse("petition_create"), data={
        "title": "Питна вода в їдальні",
        "text": "Потрібна питна вода в їдальні",
        "level": Petition.Level.CLASS,
        "deadline": (timezone.now() + timedelta(days=5)).strftime("%Y-%m-%d"),
        "class_group": class_group.id
    })
    assert response.status_code == 302
    assert Petition.objects.filter(title="Питна вода в їдальні").exists()

@pytest.mark.django_db
def test_petition_detail_view(authenticated_student, petition):
    response = authenticated_student.get(reverse("petition_detail", args=[petition.pk]))
    assert response.status_code == 200
    assert petition.title in response.content.decode()

# --- Підтримка петиції ---
@pytest.mark.django_db
def test_support_petition(authenticated_student, petition, student):
    response = authenticated_student.post(reverse("support_petition", args=[petition.pk]))
    assert response.status_code == 200
    petition.refresh_from_db()
    assert petition.supporters.filter(id=student.id).exists()

# --- Коментарі ---
@pytest.mark.django_db
def test_add_comment(authenticated_student, petition):
    response = authenticated_student.post(reverse("add_comment", args=[petition.pk]), data={
        "text": "Повністю підтримую!"
    })
    assert response.status_code == 302
    assert Comment.objects.filter(petition=petition, text="Повністю підтримую!").exists()

@pytest.mark.django_db
def test_edit_comment(authenticated_student, petition, student):
    comment = Comment.objects.create(petition=petition, author=student, text="Старий текст")
    response = authenticated_student.post(
        reverse("edit_comment", args=[petition.pk, comment.pk]),
        data={"text": "Новий текст"}
    )
    assert response.status_code == 302
    comment.refresh_from_db()
    assert comment.text == "Новий текст"

@pytest.mark.django_db
def test_delete_comment(authenticated_student, petition, student):
    comment = Comment.objects.create(petition=petition, author=student, text="Текст для видалення")
    response = authenticated_student.post(reverse("delete_comment", args=[petition.pk, comment.pk]))
    assert response.status_code == 302
    assert not Comment.objects.filter(pk=comment.pk).exists()

# --- Видалення петиції ---
@pytest.mark.django_db
def test_delete_petition(authenticated_student, petition):
    url = reverse("petition_delete", args=[petition.pk])
    response = authenticated_student.get(url)
    assert response.status_code == 302
    assert not Petition.objects.filter(pk=petition.pk).exists()

# --- Зміна статусу директором ---
@pytest.mark.django_db
def test_set_petition_status(authenticated_director, petition, director):
    petition.status = Petition.Status.PENDING
    petition.save()
    response = authenticated_director.post(reverse("petition_set_status", args=[petition.pk]), data={
        "status": Petition.Status.APPROVED
    })
    assert response.status_code == 302
    petition.refresh_from_db()
    assert petition.status == Petition.Status.APPROVED
    assert petition.reviewed_by == director
