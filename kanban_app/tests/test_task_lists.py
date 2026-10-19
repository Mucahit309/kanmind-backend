"""Tests for the personal task lists."""
from django.urls import reverse
from rest_framework import status

from .base import BoardAPITestCase, create_task


class PersonalTaskListTests(BoardAPITestCase):
    """Behaviour of the assigned-to-me and reviewing endpoints."""

    def setUp(self):
        super().setUp()
        board = self.board
        create_task(board, title="Mine", assignee=self.member)
        create_task(board, title="Review", reviewer=self.member)
        create_task(board, title="Other", assignee=self.owner)
        self.client.force_authenticate(self.member)

    def titles(self, url_name):
        """Return the task titles of the given endpoint."""
        response = self.client.get(reverse(url_name))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return [task["title"] for task in response.data]

    def test_assigned_to_me(self):
        self.assertEqual(self.titles("task-assigned-to-me"), ["Mine"])

    def test_reviewing(self):
        self.assertEqual(self.titles("task-reviewing"), ["Review"])

    def test_fields_of_a_task(self):
        response = self.client.get(reverse("task-assigned-to-me"))
        task = response.data[0]
        self.assertEqual(task["board"], self.board.id)
        self.assertEqual(task["assignee"]["id"], self.member.id)
        self.assertEqual(task["comments_count"], 0)

    def test_empty_for_other_user(self):
        self.client.force_authenticate(self.outsider)
        self.assertEqual(self.titles("task-assigned-to-me"), [])

    def test_requires_authentication(self):
        self.client.force_authenticate(None)
        for name in ("task-assigned-to-me", "task-reviewing"):
            response = self.client.get(reverse(name))
            code = response.status_code
            self.assertEqual(code, status.HTTP_401_UNAUTHORIZED)

    def test_no_general_task_list(self):
        response = self.client.get(reverse("task-list"))
        code = response.status_code
        self.assertEqual(code, status.HTTP_405_METHOD_NOT_ALLOWED)
