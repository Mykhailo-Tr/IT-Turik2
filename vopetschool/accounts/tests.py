import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from accounts.models import Student, Teacher, Parent
from schoolgroups.models import ClassGroup, TeacherGroup

User = get_user_model()

# === Fixtures ===

@pytest.fixture
def class_group(db):
    return ClassGroup.objects.create(name="7-Б")

@pytest.fixture
def teacher_group(db):
    return TeacherGroup.objects.create(name="Група фізики")

@pytest.fixture
def student_user(db, class_group):
    user = User.objects.create_user(
        email="stud@test.com", password="pass1234", role="student",
        first_name="Test", last_name="Student"
    )
    student = Student.objects.create(user=user)
    class_group.students.add(student)
    return user

@pytest.fixture
def teacher_user(db, teacher_group):
    user = User.objects.create_user(
        email="teach@test.com", password="pass1234", role="teacher",
        first_name="Test", last_name="Teacher"
    )
    teacher = Teacher.objects.create(user=user, subject="Math")
    teacher.groups.add(teacher_group)
    return user

@pytest.fixture
def parent_user(db, student_user):
    user = User.objects.create_user(
        email="parent@test.com", password="pass1234", role="parent",
        first_name="Test", last_name="Parent"
    )
    parent = Parent.objects.create(user=user)
    parent.children.add(student_user.student)
    return user

@pytest.fixture
def director_user(db):
    return User.objects.create_user(
        email="dir@test.com", password="pass1234", role="director",
        first_name="Big", last_name="Boss"
    )

@pytest.fixture
def authenticated_client(client, student_user):
    client.login(email=student_user.email, password="pass1234")
    return client

@pytest.fixture
def director_client(client, director_user):
    client.login(email=director_user.email, password="pass1234")
    return client

# === Tests ===

@pytest.mark.django_db
def test_register_redirect_invalid_role(client):
    response = client.get(reverse("register_role", args=["invalid"]))
    assert response.status_code == 302
    assert response.url == reverse("register")


@pytest.mark.django_db
def test_register_teacher_with_groups(client, teacher_group):
    url = reverse("register_role", args=["teacher"])
    data = {
        "email": "teacher2@test.com",
        "password": "securepass",
        "password2": "securepass",
        "first_name": "Ivan",
        "last_name": "Ivanov",
        "subject": "Physics",
        "groups": [teacher_group.id],
    }
    response = client.post(url, data)
    assert response.status_code == 302
    assert User.objects.filter(email="teacher2@test.com").exists()


@pytest.mark.django_db
def test_register_parent_with_children(client, student_user):
    url = reverse("register_role", args=["parent"])
    data = {
        "email": "parent2@test.com",
        "password": "securepass",
        "password2": "securepass",
        "first_name": "Oksana",
        "last_name": "Petrenko",
        "children": [student_user.student.pk],
    }
    response = client.post(url, data)
    assert response.status_code == 302
    assert User.objects.filter(email="parent2@test.com").exists()


@pytest.mark.django_db
def test_profile_view_self(authenticated_client):
    url = reverse("profile")
    response = authenticated_client.get(url)
    assert response.status_code == 200
    assert "viewed_user" in response.context


@pytest.mark.django_db
def test_profile_view_other(authenticated_client, teacher_user):
    url = reverse("user_profile", args=[teacher_user.id])
    response = authenticated_client.get(url)
    assert response.status_code == 200
    assert "viewed_user" in response.context
    assert str(teacher_user.get_full_name()) in response.content.decode()


@pytest.mark.django_db
def test_edit_profile_invalid(authenticated_client):
    url = reverse("edit_profile")
    response = authenticated_client.post(url, {
        "first_name": "",
        "last_name": ""
    })
    assert response.status_code == 200
    assert "form" in response.context


@pytest.mark.django_db
def test_delete_account_requires_login(client):
    response = client.get(reverse("delete_account"))
    assert response.status_code == 302
    assert reverse("login") in response.url


@pytest.mark.django_db
def test_delete_account_post(authenticated_client):
    url = reverse("delete_account")
    response = authenticated_client.post(url)
    assert response.status_code == 302
    assert response.url == reverse("login")
    assert not User.objects.filter(email="stud@test.com").exists()


@pytest.mark.django_db
def test_home_view_shows_votes_and_petitions(director_client):
    url = reverse("home")
    response = director_client.get(url)
    assert response.status_code == 200
    assert "votes" in response.context
    assert "petitions" in response.context


# === Additional tests ===

@pytest.mark.django_db
def test_register_student_with_class(client, class_group):
    url = reverse("register_role", args=["student"])
    data = {
        "email": "newstud@test.com",
        "password": "abc12345",
        "password2": "abc12345",
        "first_name": "New",
        "last_name": "Student",
        "class_group": class_group.id,
    }
    response = client.post(url, data)
    assert response.status_code == 302
    assert User.objects.filter(email="newstud@test.com", role="student").exists()


@pytest.mark.django_db
def test_login_wrong_password(client, student_user):
    url = reverse("login")
    response = client.post(url, {
        "username": student_user.email,
        "password": "wrongpassword"
    })
    assert response.status_code == 200
    assert "form" in response.context
    assert response.context["form"].errors


@pytest.mark.django_db
def test_register_password_mismatch(client):
    url = reverse("register_role", args=["student"])
    data = {
        "email": "test@test.com",
        "password": "onepass",
        "password2": "otherpass",
        "first_name": "Name",
        "last_name": "Surname"
    }
    response = client.post(url, data)
    assert response.status_code == 200
    assert "form" in response.context
    assert "Паролі не співпадають" in str(response.context["form"].errors)


@pytest.mark.django_db
def test_edit_profile_teacher_subject(client, teacher_user):
    client.login(email=teacher_user.email, password="pass1234")
    url = reverse("edit_profile")
    response = client.post(url, {
        "first_name": "Updated",
        "last_name": "Name",
        "email": teacher_user.email,
        "subject": "Updated Subject"
    })
    assert response.status_code == 302
    teacher_user.refresh_from_db()
    assert teacher_user.first_name == "Updated"
    assert teacher_user.teacher.subject == "Updated Subject"


@pytest.mark.django_db
def test_logout(client, student_user):
    client.login(email=student_user.email, password="pass1234")
    response = client.get(reverse("logout"))
    assert response.status_code == 302
    assert response.url == reverse("login")


@pytest.mark.django_db
def test_role_selection_post_invalid(client):
    url = reverse("register")
    response = client.post(url, {"role": "invalidrole"})
    assert response.status_code == 200
    assert "form" in response.context


@pytest.mark.django_db
def test_register_get_invalid_role(client):
    url = reverse("register_role", args=["invalid"])
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == reverse("register")
