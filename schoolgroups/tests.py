import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from schoolgroups.models import ClassGroup, TeacherGroup
from accounts.models import Teacher
from django.contrib.messages import get_messages

User = get_user_model()


@pytest.fixture
def director_user(db):
    return User.objects.create_user(email='director@test.com', password='testpass', role='director')


@pytest.fixture
def teacher_user(db):
    return User.objects.create_user(email='teacher@test.com', password='testpass', role='teacher')


@pytest.fixture
def client_logged(director_user, client):
    client.login(email=director_user.email, password='testpass')
    return client


@pytest.fixture
def teacher_group():
    return TeacherGroup.objects.create(name="Група 1")


@pytest.mark.django_db
def test_manage_classes_permission_denied(client):
    user = User.objects.create_user(email='other@test.com', password='pass', role='student')
    client.login(email='other@test.com', password='pass')
    response = client.get(reverse("manage_classes"))
    assert response.status_code == 302
    assert reverse("profile") in response.url


@pytest.mark.django_db
def test_create_class_invalid_data(client_logged):
    response = client_logged.post(reverse("create_class"), data={})
    assert response.status_code == 302
    assert ClassGroup.objects.count() == 0


@pytest.mark.django_db
def test_edit_class_empty_name(client_logged):
    class_group = ClassGroup.objects.create(name="5-Б")
    response = client_logged.post(reverse("edit_class", args=[class_group.id]), {"name": ""})
    class_group.refresh_from_db()
    assert class_group.name == "5-Б"  # не має змінюватись
    messages = list(get_messages(response.wsgi_request))
    assert any("не може бути порожньою" in str(m) for m in messages)


@pytest.mark.django_db
def test_delete_class_permission_denied(client):
    user = User.objects.create_user(email='student@test.com', password='test', role='student')
    client.login(email='student@test.com', password='test')
    class_group = ClassGroup.objects.create(name="7-В")
    response = client.post(reverse("delete_class", args=[class_group.id]))
    assert response.status_code == 302
    assert ClassGroup.objects.filter(pk=class_group.pk).exists()


@pytest.mark.django_db
def test_get_teacher_groups_requires_director(client, teacher_user):
    client.login(email=teacher_user.email, password='testpass')
    response = client.get(reverse("manage_teacher_groups"))
    assert response.status_code == 302


@pytest.mark.django_db
def test_edit_teacher_groups_valid(client_logged):
    # Створимо групу, відредагуємо її
    group = TeacherGroup.objects.create(name="Стара")
    data = {
        "edit_group-TOTAL_FORMS": "1",
        "edit_group-INITIAL_FORMS": "1",
        "edit_group-MIN_NUM_FORMS": "0",
        "edit_group-MAX_NUM_FORMS": "1000",
        "edit_group-0-id": str(group.id),
        "edit_group-0-name": "Оновлена",
        "edit_group": True,
        "edit_groups": True,
    }
    response = client_logged.post(reverse("manage_teacher_groups"), data)
    assert response.status_code == 302
    group.refresh_from_db()
    assert group.name == "Оновлена"


@pytest.mark.django_db
def test_edit_teacher_groups_invalid(client_logged):
    group = TeacherGroup.objects.create(name="First")
    data = {
        "edit_group-TOTAL_FORMS": "1",
        "edit_group-INITIAL_FORMS": "1",
        "edit_group-MIN_NUM_FORMS": "0",
        "edit_group-MAX_NUM_FORMS": "1000",
        "edit_group-0-id": str(group.id),
        "edit_group-0-name": "",  # invalid name
        "edit_groups": True,
    }
    response = client_logged.post(reverse("manage_teacher_groups"), data)
    group.refresh_from_db()
    assert group.name == "First"  # має залишитися
    messages = list(get_messages(response.wsgi_request))
    assert any("Помилка при оновленні груп" in str(m) for m in messages)


@pytest.mark.django_db
def test_delete_group_permission_denied(client):
    group = TeacherGroup.objects.create(name="Not Deletable")
    user = User.objects.create_user(email='teacher@test.com', password='pass', role='teacher')
    client.login(email='teacher@test.com', password='pass')
    response = client.post(reverse("delete_group", args=[group.id]))
    assert response.status_code == 302
    assert TeacherGroup.objects.filter(id=group.id).exists()
