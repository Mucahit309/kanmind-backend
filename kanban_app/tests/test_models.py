"""Tests for the model representations."""
from ..models import Comment
from .base import BoardAPITestCase, create_task


class ModelStrTests(BoardAPITestCase):
    """The __str__ methods return readable text."""

    def test_str_methods(self):
        task = create_task(self.board)
        comment = Comment.objects.create(
            task=task, author=self.member, content="Hi"
        )
        self.assertEqual(str(self.board), "Project X")
        self.assertEqual(str(task), "Task")
        self.assertIn(f"task {task.id}", str(comment))
