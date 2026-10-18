"""Views for boards."""
# 1. Third party
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

# 2. Local imports
from ..models import Board
from .permissions import IsBoardOwner, IsBoardOwnerOrMember
from .serializers import (
    BoardDetailSerializer,
    BoardSerializer,
    BoardUpdateSerializer,
)


class BoardViewSet(ModelViewSet):
    """List, create, show, update and delete boards."""

    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated, IsBoardOwnerOrMember]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]
    serializer_classes = {
        "retrieve": BoardDetailSerializer,
        "partial_update": BoardUpdateSerializer,
    }

    def get_queryset(self):
        """Limit the list to boards of the user; details check permissions."""
        if self.action != "list":
            return super().get_queryset()
        user = self.request.user
        return Board.objects.filter(Q(owner=user) | Q(members=user)).distinct()

    def get_serializer_class(self):
        """Pick the serializer that belongs to the current action."""
        return self.serializer_classes.get(self.action, self.serializer_class)

    def get_permissions(self):
        """Only the owner may delete a board."""
        if self.action == "destroy":
            return [IsAuthenticated(), IsBoardOwner()]
        return super().get_permissions()

    def perform_create(self, serializer):
        """Set the requesting user as owner of the new board."""
        serializer.save(owner=self.request.user)
