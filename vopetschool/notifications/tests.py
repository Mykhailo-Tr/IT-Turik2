from django.test import TestCase

# Create your tests here.
import pytest
from django.urls import reverse
from notifications.models import Notification
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.fixture
def user(db):
    return User.objects.create_user(email='test@example.com', password='testpass')

@pytest.fixture
def auth_client(client, user):
    client.login(email=user.email, password='testpass')
    return client

@pytest.fixture
def notifications(user):
    return [
        Notification.objects.create(user=user, message=f"Message {i}", link=f"/link/{i}/")
        for i in range(5)
    ]

def test_notifications_api_returns_notifications(auth_client, user, notifications):
    url = reverse('notifications_api')
    response = auth_client.get(url)

    assert response.status_code == 200
    data = response.json()
    assert "notifications" in data
    assert len(data["notifications"]) == 5

    for i, notif in enumerate(data["notifications"]):
        assert notif["message"] == f"Message {4 - i}"  # latest first
        assert notif["link"] == f"/link/{4 - i}/"

def test_notifications_api_unauthenticated(client):
    url = reverse('notifications_api')
    response = client.get(url)
    assert response.status_code == 302  # Redirect to login

def test_delete_notifications(auth_client, user, notifications):
    assert Notification.objects.filter(user=user).count() == 5

    url = reverse('delete_notifications')
    response = auth_client.get(url)
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert Notification.objects.filter(user=user).count() == 0

def test_delete_single_notification(auth_client, user):
    notif = Notification.objects.create(user=user, message="To be deleted", link="/test/")
    url = reverse('notification_delete_single')
    response = auth_client.post(
        url,
        content_type="application/json",
        data={"id": notif.id},
        HTTP_X_REQUESTED_WITH="XMLHttpRequest"
    )
    assert response.status_code == 200
    assert response.json()["status"] == "deleted"
    assert Notification.objects.filter(id=notif.id).count() == 0

def test_delete_single_notification_no_id(auth_client):
    url = reverse('notification_delete_single')
    response = auth_client.post(
        url,
        content_type="application/json",
        data={},
        HTTP_X_REQUESTED_WITH="XMLHttpRequest"
    )
    assert response.status_code == 400
    assert response.json()["status"] == "no_id_provided"

def test_delete_single_notification_invalid_json(auth_client):
    url = reverse('notification_delete_single')
    response = auth_client.post(
        url,
        content_type="application/json",
        data="not-a-json",
        HTTP_X_REQUESTED_WITH="XMLHttpRequest"
    )
    assert response.status_code == 400
    assert response.json()["status"] == "error"
