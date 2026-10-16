"""Tests for the login endpoint."""
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class LoginTests(APITestCase):
    """Behaviour of POST /api/login/."""

    def setUp(self):
        self.url = reverse("login")
        self.user = User.objects.create_user(
            username="example@mail.de",
            email="example@mail.de",
            password="examplePassword",
            first_name="Example Username",
        )
        self.payload = {
            "email": "example@mail.de",
            "password": "examplePassword",
        }

    def test_login_success(self):
        response = self.client.post(self.url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user_id"], self.user.id)
        self.assertEqual(response.data["fullname"], "Example Username")
        self.assertIn("token", response.data)

    def test_login_ignores_email_case(self):
        self.payload["email"] = "Example@Mail.de"
        response = self.client.post(self.url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_wrong_password(self):
        self.payload["password"] = "wrong"
        response = self.client.post(self.url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unknown_email(self):
        self.payload["email"] = "unknown@mail.de"
        response = self.client.post(self.url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_password(self):
        del self.payload["password"]
        response = self.client.post(self.url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
