"""Database models of the kanban app."""
from django.contrib.auth.models import User
from django.db import models


class Board(models.Model):
    """A kanban board with one owner and several members."""

    title = models.CharField(max_length=255)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="owned_boards"
    )
    members = models.ManyToManyField(
        User, related_name="member_boards", blank=True
    )

    class Meta:
        ordering = ["id"]
        verbose_name = "Board"
        verbose_name_plural = "Boards"

    def __str__(self):
        return self.title


class Task(models.Model):
    """A task that belongs to exactly one board."""

    class Status(models.TextChoices):
        TO_DO = "to-do", "To do"
        IN_PROGRESS = "in-progress", "In progress"
        REVIEW = "review", "Review"
        DONE = "done", "Done"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"

    board = models.ForeignKey(
        Board, on_delete=models.CASCADE, related_name="tasks"
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.TO_DO
    )
    priority = models.CharField(
        max_length=20, choices=Priority.choices, default=Priority.MEDIUM
    )
    assignee = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tasks",
    )
    reviewer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewing_tasks",
    )
    due_date = models.DateField(null=True, blank=True)

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_tasks",
    )

    class Meta:
        ordering = ["id"]
        verbose_name = "Task"
        verbose_name_plural = "Tasks"

    def __str__(self):
        return self.title


class Comment(models.Model):
    """A comment written by a user on a task."""

    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, related_name="comments"
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comments"
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at", "id"]
        verbose_name = "Comment"
        verbose_name_plural = "Comments"

    def __str__(self):
        return f"Comment by {self.author} on task {self.task_id}"
