"""Permissions for boards."""
from rest_framework.permissions import BasePermission


class IsBoardOwner(BasePermission):
    """Allow access only to the owner of the board."""

    def has_object_permission(self, request, view, obj):
        """Check that the user owns the board."""
        return obj.owner_id == request.user.id


class IsBoardOwnerOrMember(BasePermission):
    """Allow access to the owner and the members of the board."""

    def has_object_permission(self, request, view, obj):
        """Check that the user owns the board or is a member."""
        if obj.owner_id == request.user.id:
            return True
        return obj.members.filter(id=request.user.id).exists()
