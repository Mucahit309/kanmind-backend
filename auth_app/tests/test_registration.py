"""Tests for the registration endpoint."""
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class RegistrationTests(APITestCase):
    """Behaviour of POST /api/registration/."""

    def setUp(self):
        self.url = reverse("registration")
        self.payload = {
            "fullname": "Example Username",
            "email": "example@mail.de",
            "password": "examplePassword",
            "repeated_password": "examplePassword",
        }

    def test_registration_success(self):
        response = self.client.post(self.url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        expected = {"token", "fullname", "email", "user_id"}
        self.assertEqual(set(response.data), expected)
        self.assertEqual(response.data["fullname"], "Example Username")

    def test_registration_creates_user(self):
        self.client.post(self.url, self.payload, format="json")
        self.assertTrue(User.objects.filter(email="example@mail.de").exists())

    def test_passwords_do_not_match(self):
        self.payload["repeated_password"] = "other"
        response = self.client.post(self.url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duplicate_email_ignores_case(self):
        self.client.post(self.url, self.payload, format="json")
        self.payload["email"] = "EXAMPLE@mail.de"
        response = self.client.post(self.url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_field(self):
        del self.payload["fullname"]
        response = self.client.post(self.url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_email(self):
        self.payload["email"] = "not-an-email"
        response = self.client.post(self.url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
