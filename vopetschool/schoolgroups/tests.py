import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from schoolgroups.models import ClassGroup, TeacherGroup
from accounts.models import Teacher

User = get_user_model()


@pytest.fixture
def director_user(db):
    user = User.objects.create_user(email='director@test.com', password='testpass', role='director')
    return user


@pytest.fixture
def client_logged(director_user, client):
    client.login(email=director_user.email, password='testpass')
    return client


@pytest.mark.django_db
def test_manage_classes_view_redirects_for_non_director(client):
    user = User.objects.create_user(email='notdirector@test.com', password='pass', role='student')
    client.login(email='notdirector@test.com', password='pass')
    response = client.get(reverse("manage_classes"))
    assert response.status_code == 302
    assert reverse("profile") in response.url


@pytest.mark.django_db
def test_manage_classes_view_success(client_logged):
    response = client_logged.get(reverse("manage_classes"))
    assert response.status_code == 200
    assert "Класи" in response.content.decode()


@pytest.mark.django_db
def test_create_class_success(client_logged):
    data = {"name": "10-А"}
    response = client_logged.post(reverse("create_class"), data)
    assert response.status_code == 302
    assert ClassGroup.objects.filter(name="10-А").exists()


@pytest.mark.django_db
def test_edit_class(client_logged):
    class_group = ClassGroup.objects.create(name="Old")
    url = reverse("edit_class", args=[class_group.id])
    response = client_logged.post(url, {"name": "New"})
    assert response.status_code == 302
    class_group.refresh_from_db()
    assert class_group.name == "New"


@pytest.mark.django_db
def test_delete_class(client_logged):
    class_group = ClassGroup.objects.create(name="To Delete")
    url = reverse("delete_class", args=[class_group.id])
    response = client_logged.post(url)
    assert response.status_code == 302
    assert not ClassGroup.objects.filter(id=class_group.id).exists()


@pytest.mark.django_db
def test_manage_teacher_groups_get(client_logged):
    url = reverse("manage_teacher_groups")
    response = client_logged.get(url)
    assert response.status_code == 200
    assert "Групи вчителів" in response.content.decode()


@pytest.mark.django_db
def test_create_teacher_group(client_logged):
    data = {
        "group-name": "Нова група",
        "submit_group": True,
    }
    response = client_logged.post(reverse("manage_teacher_groups"), data)
    assert response.status_code == 302
    assert TeacherGroup.objects.filter(name="Нова група").exists()


@pytest.mark.django_db
def test_delete_teacher_group(client_logged):
    group = TeacherGroup.objects.create(name="Стара група")
    url = reverse("delete_group", args=[group.id])
    response = client_logged.post(url)
    assert response.status_code == 302
    assert not TeacherGroup.objects.filter(id=group.id).exists()
