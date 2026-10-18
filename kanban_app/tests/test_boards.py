"""Tests for listing and creating boards."""
from django.urls import reverse
from rest_framework import status

from .base import BoardAPITestCase, create_task


class BoardListTests(BoardAPITestCase):
    """Behaviour of GET /api/boards/."""

    def setUp(self):
        super().setUp()
        self.url = reverse("board-list")

    def test_requires_authentication(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_owner_and_member_see_board(self):
        for user in (self.owner, self.member):
            self.client.force_authenticate(user)
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data), 1)

    def test_outsider_sees_no_boards(self):
        self.client.force_authenticate(self.outsider)
        response = self.client.get(self.url)
        self.assertEqual(response.data, [])

    def test_counts(self):
        create_task(self.board, status="to-do", priority="high")
        create_task(self.board, status="done", priority="low")
        self.client.force_authenticate(self.owner)
        data = self.client.get(self.url).data[0]
        self.assertEqual(data["ticket_count"], 2)
        self.assertEqual(data["tasks_to_do_count"], 1)
        self.assertEqual(data["tasks_high_prio_count"], 1)
        self.assertEqual(data["member_count"], 1)


class BoardCreateTests(BoardAPITestCase):
    """Behaviour of POST /api/boards/."""

    def setUp(self):
        super().setUp()
        self.url = reverse("board-list")
        self.client.force_authenticate(self.owner)

    def test_create_success(self):
        payload = {"title": "New", "members": [self.member.id, self.owner.id]}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["owner_id"], self.owner.id)
        self.assertEqual(response.data["member_count"], 2)
        self.assertEqual(response.data["ticket_count"], 0)

    def test_create_without_members(self):
        response = self.client.post(self.url, {"title": "New"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["member_count"], 0)

    def test_create_with_unknown_member(self):
        payload = {"title": "New", "members": [9999]}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_without_title(self):
        response = self.client.post(self.url, {"members": []}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_requires_authentication(self):
        self.client.force_authenticate(None)
        response = self.client.post(self.url, {"title": "New"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
