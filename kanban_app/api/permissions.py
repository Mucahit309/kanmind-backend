"""Permissions for boards, tasks and comments."""
# 1. Third party
from django.shortcuts import get_object_or_404
from rest_framework.permissions import BasePermission

# 2. Local imports
from ..models import Board


def is_board_member(user, board):
    """Return True if the user owns the board or is one of its members."""
    if board.owner_id == user.id:
        return True
    return board.members.filter(id=user.id).exists()


class IsBoardOwner(BasePermission):
    """Allow access only to the owner of the board."""

    def has_object_permission(self, request, view, obj):
        """Check that the user owns the board."""
        return obj.owner_id == request.user.id


class IsBoardOwnerOrMember(BasePermission):
    """Allow access to the owner and the members of the board."""

    def has_object_permission(self, request, view, obj):
        """Check that the user owns the board or is a member."""
        return is_board_member(request.user, obj)


class CanCreateTask(BasePermission):
    """Creating a task needs membership in the target board."""

    def has_permission(self, request, view):
        """Check the board of a new task; other actions pass."""
        data = request.data
        if view.action != "create" or not hasattr(data, "get"):
            return True
        board_id = str(data.get("board"))
        if not board_id.isdecimal():
            return True
        board = get_object_or_404(Board, pk=int(board_id))
        return is_board_member(request.user, board)


class IsTaskBoardMember(BasePermission):
    """Allow access to members of the board the task belongs to."""

    def has_object_permission(self, request, view, obj):
        """Check membership in the board of the task."""
        return is_board_member(request.user, obj.board)


class IsTaskCreatorOrBoardOwner(BasePermission):
    """Allow the creator of a task and the board owner."""

    def has_object_permission(self, request, view, obj):
        """Check that the user created the task or owns its board."""
        return request.user.id in (obj.created_by_id, obj.board.owner_id)


class IsCommentTaskBoardMember(BasePermission):
    """Allow listing and creating comments for members of the board."""

    def has_permission(self, request, view):
        """Check membership in the board of the task from the URL."""
        task = view.get_task()
        return is_board_member(request.user, task.board)


class IsCommentAuthor(BasePermission):
    """Allow only the author of a comment."""

    def has_object_permission(self, request, view, obj):
        """Check that the user wrote the comment."""
        return obj.author_id == request.user.id
