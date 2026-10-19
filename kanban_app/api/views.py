"""Views for boards, tasks and comments."""
# 1. Third party
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    UpdateModelMixin,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet

# 2. Local imports
from ..models import Board, Comment, Task
from .permissions import (
    CanCreateTask,
    IsBoardOwner,
    IsBoardOwnerOrMember,
    IsCommentAuthor,
    IsCommentTaskBoardMember,
    IsTaskBoardMember,
    IsTaskCreatorOrBoardOwner,
)
from .serializers import (
    BoardDetailSerializer,
    BoardSerializer,
    BoardUpdateSerializer,
    CommentSerializer,
    TaskSerializer,
    TaskUpdateSerializer,
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


class TaskViewSet(
    CreateModelMixin, UpdateModelMixin, DestroyModelMixin, GenericViewSet
):
    """Create, update and delete tasks; list the personal task lists.

    There is no general task list, because it would expose the tasks of
    boards the user does not belong to.
    """

    queryset = Task.objects.select_related("board", "assignee", "reviewer")
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, CanCreateTask]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_serializer_class(self):
        """Use the update serializer for PATCH requests."""
        if self.action == "partial_update":
            return TaskUpdateSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        """Pick the permissions that belong to the current action."""
        if self.action == "partial_update":
            return [IsAuthenticated(), IsTaskBoardMember()]
        if self.action == "destroy":
            return [IsAuthenticated(), IsTaskCreatorOrBoardOwner()]
        return super().get_permissions()

    def perform_create(self, serializer):
        """Remember who created the task."""
        serializer.save(created_by=self.request.user)

    @action(detail=False, url_path="assigned-to-me")
    def assigned_to_me(self, request):
        """List the tasks assigned to the current user."""
        tasks = self.get_queryset().filter(assignee=request.user)
        return Response(self.get_serializer(tasks, many=True).data)

    @action(detail=False)
    def reviewing(self, request):
        """List the tasks the current user has to review."""
        tasks = self.get_queryset().filter(reviewer=request.user)
        return Response(self.get_serializer(tasks, many=True).data)


class TaskCommentViewSet(ModelViewSet):
    """List, create and delete the comments of one task."""

    queryset = Comment.objects.select_related("author")
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsCommentTaskBoardMember]
    http_method_names = ["get", "post", "delete", "head", "options"]
    _task = None

    def get_task(self):
        """Return the task from the URL (cached) or raise a 404."""
        if self._task is None:
            self._task = get_object_or_404(Task, pk=self.kwargs["task_id"])
        return self._task

    def get_queryset(self):
        """Return only the comments of the task from the URL."""
        return super().get_queryset().filter(task=self.get_task())

    def get_permissions(self):
        """Only the author may delete a comment."""
        if self.action == "destroy":
            return [IsAuthenticated(), IsCommentAuthor()]
        return super().get_permissions()

    def perform_create(self, serializer):
        """Set task and author of the new comment."""
        serializer.save(task=self.get_task(), author=self.request.user)
