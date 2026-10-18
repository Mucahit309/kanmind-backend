"""Tests for showing, updating and deleting a single board."""
from rest_framework import status

from ..models import Board, Comment, Task
from .base import BoardAPITestCase, create_task


class BoardRetrieveTests(BoardAPITestCase):
    """Behaviour of GET /api/boards/{id}/."""

    def test_owner_and_member_allowed(self):
        for user in (self.owner, self.member):
            self.client.force_authenticate(user)
            response = self.client.get(self.detail_url())
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_outsider_forbidden(self):
        self.client.force_authenticate(self.outsider)
        response = self.client.get(self.detail_url())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unknown_board(self):
        self.client.force_authenticate(self.owner)
        response = self.client.get(self.detail_url(9999))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_requires_authentication(self):
        response = self.client.get(self.detail_url())
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_contains_members_and_tasks(self):
        task = create_task(self.board, assignee=self.member)
        Comment.objects.create(task=task, author=self.owner, content="Hi")
        self.client.force_authenticate(self.owner)
        data = self.client.get(self.detail_url()).data
        self.assertEqual(data["owner_id"], self.owner.id)
        self.assertEqual(data["members"][0]["fullname"], "Member")
        self.assertEqual(data["tasks"][0]["assignee"]["id"], self.member.id)
        self.assertIsNone(data["tasks"][0]["reviewer"])
        self.assertEqual(data["tasks"][0]["comments_count"], 1)


class BoardUpdateTests(BoardAPITestCase):
    """Behaviour of PATCH /api/boards/{id}/."""

    def test_member_updates_title_and_members(self):
        self.client.force_authenticate(self.member)
        payload = {"title": "Changed", "members": [self.outsider.id]}
        response = self.client.patch(self.detail_url(), payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Changed")
        self.assertEqual(response.data["owner_data"]["id"], self.owner.id)
        ids = [user["id"] for user in response.data["members_data"]]
        self.assertEqual(ids, [self.outsider.id])

    def test_outsider_forbidden(self):
        self.client.force_authenticate(self.outsider)
        response = self.client.patch(
            self.detail_url(), {"title": "Hack"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unknown_member(self):
        self.client.force_authenticate(self.owner)
        response = self.client.patch(
            self.detail_url(), {"members": [9999]}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unknown_board(self):
        self.client.force_authenticate(self.owner)
        response = self.client.patch(
            self.detail_url(9999), {"title": "X"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_put_not_allowed(self):
        self.client.force_authenticate(self.owner)
        response = self.client.put(
            self.detail_url(), {"title": "X"}, format="json"
        )
        self.assertEqual(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )


class BoardDeleteTests(BoardAPITestCase):
    """Behaviour of DELETE /api/boards/{id}/."""

    def test_owner_deletes_board(self):
        self.client.force_authenticate(self.owner)
        response = self.client.delete(self.detail_url())
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Board.objects.filter(id=self.board.id).exists())

    def test_member_cannot_delete(self):
        self.client.force_authenticate(self.member)
        response = self.client.delete(self.detail_url())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Board.objects.filter(id=self.board.id).exists())

    def test_outsider_cannot_delete(self):
        self.client.force_authenticate(self.outsider)
        response = self.client.delete(self.detail_url())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unknown_board(self):
        self.client.force_authenticate(self.owner)
        response = self.client.delete(self.detail_url(9999))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_removes_tasks(self):
        create_task(self.board)
        self.client.force_authenticate(self.owner)
        self.client.delete(self.detail_url())
        self.assertEqual(Task.objects.count(), 0)
