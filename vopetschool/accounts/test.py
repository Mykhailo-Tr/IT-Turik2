from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from accounts.models import User
from accounts.forms import RoleChoiceForm

UserModel = get_user_model()

class AccountViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.student_data = {
            "email": "student@example.com",
            "first_name": "Test",
            "last_name": "Student",
            "password1": "Testpass123",
            "password2": "Testpass123",
            "school_class": "10-Б",
        }

        self.director_data = {
            "email": "director@example.com",
            "first_name": "Dina", 
            "last_name": "Director",
            "password1": "Testpass123",
            "password2": "Testpass123",
        }

    def test_role_select_get(self):
        response = self.client.get(reverse("register"))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context["form"], RoleChoiceForm)

    def test_role_select_post_redirect(self):
        response = self.client.post(reverse("register"), data={"role": "student"})
        self.assertRedirects(response, "/accounts/register/student/")

    def test_register_student(self):
        response = self.client.post(reverse("register_with_role", args=["student"]), data=self.student_data)
        self.assertEqual(response.status_code, 302)  # redirect after login
        self.assertTrue(UserModel.objects.filter(email="student@example.com").exists())

    def test_register_director(self):
        response = self.client.post(reverse("register_with_role", args=["director"]), data=self.director_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(UserModel.objects.filter(email="director@example.com", role="director").exists())

    def test_login_logout_flow(self):
        user = UserModel.objects.create_user(email="testuser@example.com", password="Testpass123")
        login = self.client.login(email="testuser@example.com", password="Testpass123")
        self.assertTrue(login)

        response = self.client.get(reverse("logout"))
        self.assertRedirects(response, reverse("login"))

    def test_profile_view_authenticated(self):
        user = UserModel.objects.create_user(email="profile@example.com", password="Testpass123")
        self.client.login(email="profile@example.com", password="Testpass123")
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/profile.html")

    def test_profile_view_unauthenticated(self):
        response = self.client.get(reverse("profile"))
        self.assertRedirects(response, f'/accounts/login/?next=/accounts/profile/')

    def test_delete_account_view(self):
        user = UserModel.objects.create_user(email="delete@example.com", password="Testpass123")
        self.client.login(email="delete@example.com", password="Testpass123")

        # GET confirmation page
        response = self.client.get(reverse("delete_account"))
        self.assertEqual(response.status_code, 200)

        # POST delete
        response = self.client.post(reverse("delete_account"))
        self.assertRedirects(response, reverse("login"))
        self.assertFalse(UserModel.objects.filter(email="delete@example.com").exists())
