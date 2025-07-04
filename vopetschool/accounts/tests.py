import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import Client
from accounts.models import ClassGroup, Student

User = get_user_model()

# ==== FIXTURES ====

@pytest.fixture
def client():
    return Client()

@pytest.fixture
def student(db):
    student = User.objects.create_user(
        email="student@example.com",
        password="password123",
        role=User.Role.STUDENT,
        first_name="Ivan",
        last_name="Petrenko"
    )
    Student.objects.create(user=student)
    return student

@pytest.fixture
def authenticated_client(client, student):
    client.force_login(student)
    return client

# ==== TESTS ====

@pytest.mark.django_db
def test_register_role_selection_view(client):
    url = reverse("register")
    response = client.get(url)
    assert response.status_code == 200
    assert "form" in response.context

    # Valid role selection POST
    response = client.post(url, {"role": "student"})
    assert response.status_code == 302
    assert response.url == reverse("register_role", args=["student"])

    # Invalid role selection POST
    response = client.post(url, {"role": ""})
    assert response.status_code == 200
    assert "form" in response.context


@pytest.mark.django_db
def test_register_view_get(client):
    url = reverse("register_role", args=["student"])
    response = client.get(url)
    assert response.status_code == 200
    assert "form" in response.context

@pytest.mark.django_db
def test_register_view_post_valid(client):
    url = reverse("register_role", args=["student"])
    school_class = ClassGroup.objects.create(name="Test Class")  # Приклад класу, якщо потрібно
    data = {
        "email": "newstudent@example.com",
        "password": "Testpass123",
        "password2": "Testpass123",
        "first_name": "Test",
        "last_name": "User",
        "role": "student",  # можливо не потрібно, якщо визначається з URL
        "school_class": school_class.id
    }
    response = client.post(url, data)
    
    if response.status_code == 200:
        # DEBUG: показати помилки форми
        print("Form errors:", response.context["form"].errors)
    assert response.status_code == 302
    assert response.url == reverse("profile")
    assert User.objects.filter(email="newstudent@example.com").exists()


@pytest.mark.django_db
def test_register_view_post_invalid(client):
    url = reverse("register_role", args=["student"])
    data = {
        "email": "",
        "password1": "pass",
        "password2": "pass"
    }
    response = client.post(url, data)
    assert response.status_code == 200
    assert "form" in response.context


@pytest.mark.django_db
def test_login_valid(client, student):
    url = reverse("login")
    response = client.post(url, {
        "username": student.email,
        "password": "password123"
    })
    assert response.status_code == 302
    assert response.url == reverse("profile")


@pytest.mark.django_db
def test_login_invalid(client):
    url = reverse("login")
    response = client.post(url, {
        "username": "wrong@example.com",
        "password": "wrongpass"
    })
    assert response.status_code == 200
    assert "form" in response.context


@pytest.mark.django_db
def test_logout_view(authenticated_client):
    url = reverse("logout")
    response = authenticated_client.get(url)
    assert response.status_code == 302
    assert response.url == reverse("login")


@pytest.mark.django_db
def test_profile_view_requires_login(client):
    url = reverse("profile")
    response = client.get(url)
    assert response.status_code == 302
    assert response.url.startswith(reverse("login"))


@pytest.mark.django_db
def test_profile_view_authenticated(authenticated_client):
    url = reverse("profile")
    response = authenticated_client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_edit_profile_get(authenticated_client):
    url = reverse("edit_profile")
    response = authenticated_client.get(url)
    assert response.status_code == 200
    assert "form" in response.context


@pytest.mark.django_db
def test_edit_profile_post_valid(authenticated_client):
    url = reverse("edit_profile")
    response = authenticated_client.post(url, {
        "first_name": "New",
        "last_name": "Name",
        "email": "student@example.com"
    })
    assert response.status_code == 302
    assert response.url == reverse("profile")
    user = User.objects.get(email="student@example.com")
    assert user.first_name == "New"


@pytest.mark.django_db
def test_edit_profile_post_invalid(authenticated_client):
    url = reverse("edit_profile")
    response = authenticated_client.post(url, {
        "first_name": "",
        "last_name": ""
    })
    assert response.status_code == 200
    assert "form" in response.context


@pytest.mark.django_db
def test_delete_account_get_requires_auth(client):
    url = reverse("delete_account")
    response = client.get(url)
    assert response.status_code == 302
    assert response.url.startswith(reverse("login"))


@pytest.mark.django_db
def test_delete_account_get_authenticated(authenticated_client):
    url = reverse("delete_account")
    response = authenticated_client.get(url)
    assert response.status_code == 200
    assert "user" in response.context


@pytest.mark.django_db
def test_delete_account_post(authenticated_client):
    url = reverse("delete_account")
    response = authenticated_client.post(url)
    assert response.status_code == 302
    assert response.url == reverse("login")
    assert not User.objects.filter(email="student@example.com").exists()