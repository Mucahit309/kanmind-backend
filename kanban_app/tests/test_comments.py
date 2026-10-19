"""Tests for the comments of a task."""
from django.urls import reverse
from rest_framework import status

from ..models import Comment
from .base import BoardAPITestCase, create_comment, create_task


class CommentListTests(BoardAPITestCase):
    """Behaviour of GET /api/tasks/{id}/comments/."""

    def setUp(self):
        super().setUp()
        self.task = create_task(self.board)
        self.url = reverse("task-comments", args=[self.task.id])

    def test_list_in_chronological_order(self):
        create_comment(self.task, self.owner, "First")
        create_comment(self.task, self.member, "Second")
        self.client.force_authenticate(self.member)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        contents = [item["content"] for item in response.data]
        self.assertEqual(contents, ["First", "Second"])
        self.assertEqual(response.data[0]["author"], "Owner")

    def test_owner_allowed(self):
        self.client.force_authenticate(self.owner)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_outsider_forbidden(self):
        self.client.force_authenticate(self.outsider)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unknown_task(self):
        self.client.force_authenticate(self.member)
        response = self.client.get(reverse("task-comments", args=[9999]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_requires_authentication(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CommentCreateTests(BoardAPITestCase):
    """Behaviour of POST /api/tasks/{id}/comments/."""

    def setUp(self):
        super().setUp()
        self.task = create_task(self.board)
        self.url = reverse("task-comments", args=[self.task.id])
        self.client.force_authenticate(self.member)

    def post(self, data, url=None):
        """Send a POST request with JSON data."""
        return self.client.post(url or self.url, data, format="json")

    def test_create_success(self):
        response = self.post({"content": "Hello"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["author"], "Member")
        self.assertEqual(response.data["content"], "Hello")
        self.assertIn("created_at", response.data)
        self.assertEqual(Comment.objects.get().author, self.member)

    def test_empty_or_missing_content(self):
        for data in ({"content": ""}, {}):
            response = self.post(data)
            code = response.status_code
            self.assertEqual(code, status.HTTP_400_BAD_REQUEST)

    def test_outsider_forbidden(self):
        self.client.force_authenticate(self.outsider)
        response = self.post({"content": "Hello"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unknown_task(self):
        url = reverse("task-comments", args=[9999])
        response = self.post({"content": "Hello"}, url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_requires_authentication(self):
        self.client.force_authenticate(None)
        response = self.post({"content": "Hello"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CommentDeleteTests(BoardAPITestCase):
    """Behaviour of DELETE /api/tasks/{id}/comments/{id}/."""

    def setUp(self):
        super().setUp()
        self.task = create_task(self.board)
        self.comment = create_comment(self.task, self.member)
        self.client.force_authenticate(self.member)

    def delete(self, task_id=None, comment_id=None):
        """Send a DELETE request for the given or the default ids."""
        url = reverse(
            "task-comment-detail",
            args=[task_id or self.task.id, comment_id or self.comment.id],
        )
        return self.client.delete(url)

    def test_author_deletes(self):
        response = self.delete()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Comment.objects.filter(id=self.comment.id).exists())

    def test_board_owner_cannot_delete(self):
        self.client.force_authenticate(self.owner)
        response = self.delete()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unknown_comment(self):
        response = self.delete(comment_id=9999)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_comment_of_another_task(self):
        other_task = create_task(self.board)
        response = self.delete(task_id=other_task.id)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unknown_task(self):
        response = self.delete(task_id=9999)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_requires_authentication(self):
        self.client.force_authenticate(None)
        response = self.delete()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
