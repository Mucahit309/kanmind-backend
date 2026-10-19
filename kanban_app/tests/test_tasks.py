"""Tests for creating, updating and deleting tasks."""
from django.urls import reverse
from rest_framework import status

from ..models import Board, Task
from .base import BoardAPITestCase, create_task


class TaskCreateTests(BoardAPITestCase):
    """Behaviour of POST /api/tasks/."""

    def setUp(self):
        super().setUp()
        self.url = reverse("task-list")
        self.client.force_authenticate(self.member)

    def payload(self, **overrides):
        """Return a valid request body with optional overrides."""
        data = {
            "board": self.board.id,
            "title": "New task",
            "description": "Some text",
            "status": "review",
            "priority": "medium",
            "assignee_id": self.member.id,
            "reviewer_id": self.owner.id,
            "due_date": "2025-02-27",
        }
        data.update(overrides)
        return data

    def post(self, data):
        """Send a POST request with JSON data."""
        return self.client.post(self.url, data, format="json")

    def test_create_success(self):
        response = self.post(self.payload())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["board"], self.board.id)
        self.assertEqual(response.data["assignee"]["id"], self.member.id)
        self.assertEqual(response.data["reviewer"]["fullname"], "Owner")
        self.assertEqual(response.data["comments_count"], 0)

    def test_creator_is_saved(self):
        self.post(self.payload())
        self.assertEqual(Task.objects.get().created_by, self.member)

    def test_owner_can_create(self):
        self.client.force_authenticate(self.owner)
        response = self.post(self.payload())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_without_people(self):
        response = self.post({"board": self.board.id, "title": "Minimal"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNone(response.data["assignee"])
        self.assertIsNone(response.data["reviewer"])

    def test_outsider_forbidden(self):
        self.client.force_authenticate(self.outsider)
        response = self.post(self.payload())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unknown_board(self):
        response = self.post(self.payload(board=9999))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_missing_board(self):
        data = self.payload()
        del data["board"]
        response = self.post(data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_body_is_not_an_object(self):
        response = self.post([1, 2])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_values(self):
        invalid = [
            {"title": ""},
            {"status": "unknown"},
            {"priority": "urgent"},
            {"due_date": "not-a-date"},
            {"assignee_id": self.outsider.id},
            {"reviewer_id": self.outsider.id},
            {"assignee_id": 9999},
        ]
        for overrides in invalid:
            response = self.post(self.payload(**overrides))
            code = response.status_code
            self.assertEqual(code, status.HTTP_400_BAD_REQUEST)

    def test_requires_authentication(self):
        self.client.force_authenticate(None)
        response = self.post(self.payload())
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TaskUpdateTests(BoardAPITestCase):
    """Behaviour of PATCH /api/tasks/{id}/."""

    def setUp(self):
        super().setUp()
        self.task = create_task(self.board, assignee=self.member)
        self.url = reverse("task-detail", args=[self.task.id])
        self.client.force_authenticate(self.member)

    def patch(self, data, url=None):
        """Send a PATCH request with JSON data."""
        return self.client.patch(url or self.url, data, format="json")

    def test_update_success(self):
        response = self.patch({"title": "Changed", "status": "done"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Changed")
        self.assertEqual(response.data["status"], "done")
        self.assertNotIn("board", response.data)
        self.assertEqual(response.data["assignee"]["id"], self.member.id)

    def test_clear_assignee(self):
        response = self.patch({"assignee_id": None})
        self.assertIsNone(response.data["assignee"])

    def test_set_reviewer(self):
        response = self.patch({"reviewer_id": self.owner.id})
        self.assertEqual(response.data["reviewer"]["id"], self.owner.id)

    def test_same_board_is_allowed(self):
        response = self.patch({"board": self.board.id, "title": "Same"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_board_change_is_rejected(self):
        other = Board.objects.create(title="Other", owner=self.owner)
        response = self.patch({"board": other.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_people_must_be_members(self):
        response = self.patch({"assignee_id": self.outsider.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_status(self):
        response = self.patch({"status": "unknown"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_outsider_forbidden(self):
        self.client.force_authenticate(self.outsider)
        response = self.patch({"title": "Hack"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unknown_task(self):
        url = reverse("task-detail", args=[9999])
        response = self.patch({"title": "X"}, url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_requires_authentication(self):
        self.client.force_authenticate(None)
        response = self.patch({"title": "X"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_put_not_allowed(self):
        response = self.client.put(self.url, {"title": "X"}, format="json")
        code = response.status_code
        self.assertEqual(code, status.HTTP_405_METHOD_NOT_ALLOWED)


class TaskDeleteTests(BoardAPITestCase):
    """Behaviour of DELETE /api/tasks/{id}/."""

    def setUp(self):
        super().setUp()
        self.task = create_task(self.board, created_by=self.member)
        self.url = reverse("task-detail", args=[self.task.id])

    def delete_as(self, user):
        """Send a DELETE request as the given user."""
        self.client.force_authenticate(user)
        return self.client.delete(self.url)

    def test_creator_deletes(self):
        response = self.delete_as(self.member)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Task.objects.filter(id=self.task.id).exists())

    def test_board_owner_deletes(self):
        response = self.delete_as(self.owner)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_other_member_forbidden(self):
        self.board.members.add(self.outsider)
        response = self.delete_as(self.outsider)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Task.objects.filter(id=self.task.id).exists())

    def test_outsider_forbidden(self):
        response = self.delete_as(self.outsider)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_task_without_creator(self):
        Task.objects.filter(id=self.task.id).update(created_by=None)
        member_response = self.delete_as(self.member)
        owner_response = self.delete_as(self.owner)
        self.assertEqual(member_response.status_code, 403)
        self.assertEqual(owner_response.status_code, 204)

    def test_unknown_task(self):
        self.url = reverse("task-detail", args=[9999])
        response = self.delete_as(self.owner)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_requires_authentication(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
