"""Shared helpers for the kanban app tests."""
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase

from ..models import Board, Task


def create_user(email, fullname="Test User"):
    """Create a user the same way the registration does."""
    return User.objects.create_user(
        username=email,
        email=email,
        password="testPass123",
        first_name=fullname,
    )


def create_task(board, **kwargs):
    """Create a task on the given board with default values."""
    data = {"title": "Task", "description": "Some text"}
    data.update(kwargs)
    return Task.objects.create(board=board, **data)


class BoardAPITestCase(APITestCase):
    """Base class with an owner, a member, an outsider and one board."""

    def setUp(self):
        self.owner = create_user("owner@mail.de", "Owner")
        self.member = create_user("member@mail.de", "Member")
        self.outsider = create_user("outsider@mail.de", "Outsider")
        self.board = Board.objects.create(title="Project X", owner=self.owner)
        self.board.members.add(self.member)

    def detail_url(self, board_id=None):
        """Return the detail URL of the given or the default board."""
        return reverse("board-detail", args=[board_id or self.board.id])
