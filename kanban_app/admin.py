"""Admin configuration of the kanban app."""
from django.contrib import admin

from .models import Board, Comment, Task


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    """Admin view of boards."""

    list_display = ["id", "title", "owner"]
    filter_horizontal = ["members"]


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Admin view of tasks."""

    list_display = ["id", "title", "board", "status", "priority"]
    list_filter = ["status", "priority"]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Admin view of comments."""

    list_display = ["id", "task", "author", "created_at"]
