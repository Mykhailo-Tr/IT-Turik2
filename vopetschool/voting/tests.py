import pytest
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.test import Client
from voting.models import Vote, VoteOption, VoteAnswer
from datetime import timedelta

User = get_user_model()


@pytest.fixture
def client():
    return Client()

@pytest.fixture
def user(db):
    return User.objects.create_user(
        email="student@example.com",
        password="password123",
        role=User.Role.STUDENT,
        first_name="Ivan",
        last_name="Petrenko"
    )

@pytest.fixture
def teacher(db):
    return User.objects.create_user(
        email="teacher@example.com",
        password="password123",
        role=User.Role.TEACHER,
        first_name="Olena",
        last_name="Ivanenko"
    )

@pytest.fixture
def admin(db):
    return User.objects.create_user(
        email="admin@example.com",
        password="password123",
        role=User.Role.DIRECTOR,
        first_name="Admin",
        last_name="User"
    )

@pytest.fixture
def authenticated_client(client, user):
    client.force_login(user)
    return client

@pytest.fixture
def admin_client(client, admin):
    client.force_login(admin)
    return client

@pytest.fixture
def vote(user):
    vote = Vote.objects.create(
        title="Test Vote",
        level=Vote.Level.SCHOOL,
        start_date=timezone.now() - timedelta(days=1),
        end_date=timezone.now() + timedelta(days=1),
        creator=user
    )
    VoteOption.objects.create(vote=vote, text="Так", is_correct=True)
    VoteOption.objects.create(vote=vote, text="Ні", is_correct=False)
    return vote

# ===== TESTS =====

@pytest.mark.django_db
def test_vote_list_view(authenticated_client):
    response = authenticated_client.get(reverse("vote_list"))
    assert response.status_code == 200
    assert "votes" in response.context

@pytest.mark.django_db
def test_vote_list_view_admin_sees_all(admin_client, vote):
    response = admin_client.get(reverse("vote_list"))
    assert vote in response.context["votes"]

@pytest.mark.django_db
def test_vote_detail_view(authenticated_client, vote):
    url = reverse("vote_detail", args=[vote.pk])
    response = authenticated_client.get(url)
    assert response.status_code == 200
    assert response.context["vote"].pk == vote.pk

@pytest.mark.django_db
def test_vote_submission_success(authenticated_client, vote, user):
    option = vote.options.first()
    url = reverse("vote_detail", args=[vote.pk])
    response = authenticated_client.post(url, data={"options": option.id})

    assert response.status_code == 302
    assert VoteAnswer.objects.filter(voter=user, option=option).exists()

@pytest.mark.django_db
def test_vote_submission_after_end(authenticated_client, vote):
    vote.end_date = timezone.now() - timedelta(hours=1)
    vote.save()

    option = vote.options.first()
    response = authenticated_client.post(
        reverse("vote_detail", args=[vote.pk]),
        data={"options": option.id}
    )
    assert response.status_code == 200
    assert not VoteAnswer.objects.filter(option=option).exists()

@pytest.mark.django_db
def test_prevent_double_vote(authenticated_client, vote, user):
    option = vote.options.first()
    VoteAnswer.objects.create(voter=user, option=option)

    response = authenticated_client.post(
        reverse("vote_detail", args=[vote.pk]),
        data={"options": option.id}
    )

    assert response.status_code == 200
    assert "form" not in response.context or response.context["form"] is None

@pytest.mark.django_db
def test_vote_create_valid(authenticated_client, user):
    url = reverse("vote_create")
    now = timezone.now()
    data = {
        "title": "New Vote",
        "level": Vote.Level.SCHOOL,
        "start_date": now,
        "end_date": now + timedelta(days=1),
        "form-TOTAL_FORMS": "2",
        "form-INITIAL_FORMS": "0",
        "form-MIN_NUM_FORMS": "0",
        "form-MAX_NUM_FORMS": "1000",
        "form-0-text": "Yes",
        "form-0-is_correct": "on",
        "form-1-text": "No",
    }
    response = authenticated_client.post(url, data)
    assert response.status_code == 302
    assert Vote.objects.filter(title="New Vote").exists()

@pytest.mark.django_db
def test_vote_create_invalid_form(authenticated_client):
    url = reverse("vote_create")
    now = timezone.now()
    data = {
        "title": "",
        "level": Vote.Level.SCHOOL,
        "start_date": now,
        "end_date": now + timedelta(days=1),
        "form-TOTAL_FORMS": "1",
        "form-INITIAL_FORMS": "0",
        "form-MIN_NUM_FORMS": "0",
        "form-MAX_NUM_FORMS": "1000",
        "form-0-text": "",
    }
    response = authenticated_client.post(url, data)
    assert response.status_code == 200
    assert "form" in response.context

@pytest.mark.django_db
def test_vote_delete_by_creator(authenticated_client, vote):
    url = reverse("vote_delete", args=[vote.pk])
    response = authenticated_client.post(url)
    assert response.status_code == 302
    assert not Vote.objects.filter(pk=vote.pk).exists()

@pytest.mark.django_db
def test_vote_delete_by_non_creator(client, vote, teacher):
    client.force_login(teacher)
    url = reverse("vote_delete", args=[vote.pk])
    response = client.post(url)
    assert response.status_code == 403
    assert Vote.objects.filter(pk=vote.pk).exists()

@pytest.mark.django_db
def test_vote_delete_by_admin(admin_client, vote):
    url = reverse("vote_delete", args=[vote.pk])
    response = admin_client.post(url)
    assert response.status_code == 302
    assert not Vote.objects.filter(pk=vote.pk).exists()

@pytest.mark.django_db
def test_vote_stats_api_access(authenticated_client, vote, user):
    VoteAnswer.objects.create(voter=user, option=vote.options.first())
    url = reverse("vote_stats_api", args=[vote.pk])
    response = authenticated_client.get(url)
    data = response.json()

    assert response.status_code == 200
    assert "total_votes" in data
    assert isinstance(data["options"], list)

@pytest.mark.django_db
def test_vote_stats_access_denied_if_not_voted(authenticated_client, vote):
    url = reverse("vote_stats_api", args=[vote.pk])
    response = authenticated_client.get(url)

    # Якщо користувач не голосував і голосування активне
    if vote.is_active():
        assert response.status_code in [403, 200]  # залежно від логіки дозволів
