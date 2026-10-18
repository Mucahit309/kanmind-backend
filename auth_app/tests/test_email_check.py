"""Tests for the email check endpoint."""
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class EmailCheckTests(APITestCase):
    """Behaviour of GET /api/email-check/."""

    def setUp(self):
        self.url = reverse("email-check")
        self.user = User.objects.create_user(
            username="max@mail.de",
            email="max@mail.de",
            password="testPass123",
            first_name="Max Mustermann",
        )
        self.client.force_authenticate(self.user)

    def test_existing_email(self):
        response = self.client.get(self.url, {"email": "max@mail.de"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {
                "id": self.user.id,
                "email": "max@mail.de",
                "fullname": "Max Mustermann",
            },
        )

    def test_email_ignores_case(self):
        response = self.client.get(self.url, {"email": "MAX@mail.de"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unknown_email(self):
        response = self.client.get(self.url, {"email": "none@mail.de"})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_missing_email(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_email(self):
        response = self.client.get(self.url, {"email": "abc"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_requires_authentication(self):
        self.client.force_authenticate(None)
        response = self.client.get(self.url, {"email": "max@mail.de"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
