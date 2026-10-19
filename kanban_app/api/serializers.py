"""Serializers for boards, tasks and comments."""
# 1. Third party
from django.contrib.auth.models import User
from rest_framework import serializers

# 2. Local imports
from auth_app.api.serializers import UserSummarySerializer
from ..models import Board, Comment, Task
from .permissions import is_board_member


def members_field():
    """Return a write-only field that accepts a list of user ids."""
    return serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        write_only=True,
        required=False,
    )


def person_field(source):
    """Return a write-only field that accepts one user id or null."""
    return serializers.PrimaryKeyRelatedField(
        source=source,
        queryset=User.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )


class BoardTaskSerializer(serializers.ModelSerializer):
    """Task representation inside the board detail."""

    assignee = UserSummarySerializer(read_only=True)
    reviewer = UserSummarySerializer(read_only=True)
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "status",
            "priority",
            "assignee",
            "reviewer",
            "due_date",
            "comments_count",
        ]

    def get_comments_count(self, obj):
        """Return the number of comments of the task."""
        return obj.comments.count()


class BoardSerializer(serializers.ModelSerializer):
    """Board summary used for the list and for creating boards."""

    owner_id = serializers.ReadOnlyField()
    members = members_field()
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = [
            "id",
            "title",
            "members",
            "member_count",
            "ticket_count",
            "tasks_to_do_count",
            "tasks_high_prio_count",
            "owner_id",
        ]

    def get_member_count(self, obj):
        """Return the number of board members."""
        return obj.members.count()

    def get_ticket_count(self, obj):
        """Return the number of tasks on the board."""
        return obj.tasks.count()

    def get_tasks_to_do_count(self, obj):
        """Return the number of tasks with status to-do."""
        return obj.tasks.filter(status=Task.Status.TO_DO).count()

    def get_tasks_high_prio_count(self, obj):
        """Return the number of tasks with high priority."""
        return obj.tasks.filter(priority=Task.Priority.HIGH).count()


class BoardDetailSerializer(serializers.ModelSerializer):
    """Board with all members and tasks."""

    owner_id = serializers.ReadOnlyField()
    members = UserSummarySerializer(many=True, read_only=True)
    tasks = BoardTaskSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = ["id", "title", "owner_id", "members", "tasks"]


class BoardUpdateSerializer(serializers.ModelSerializer):
    """Update title and members of a board."""

    members = members_field()
    owner_data = UserSummarySerializer(source="owner", read_only=True)
    members_data = UserSummarySerializer(
        source="members", many=True, read_only=True
    )

    class Meta:
        model = Board
        fields = ["id", "title", "members", "owner_data", "members_data"]


class TaskPeopleSerializer(serializers.ModelSerializer):
    """Base class: assignee and reviewer as ids in, as objects out."""

    assignee = UserSummarySerializer(read_only=True)
    reviewer = UserSummarySerializer(read_only=True)
    assignee_id = person_field("assignee")
    reviewer_id = person_field("reviewer")

    def validate(self, attrs):
        """Ensure assignee and reviewer are members of the board."""
        board = attrs.get("board") or self.instance.board
        for name in ("assignee", "reviewer"):
            user = attrs.get(name)
            if user and not is_board_member(user, board):
                raise serializers.ValidationError(
                    {f"{name}_id": "User is not a member of the board."}
                )
        return attrs


class TaskSerializer(TaskPeopleSerializer):
    """Full task used for creating tasks and for the personal lists."""

    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            "id",
            "board",
            "title",
            "description",
            "status",
            "priority",
            "assignee",
            "reviewer",
            "assignee_id",
            "reviewer_id",
            "due_date",
            "comments_count",
        ]

    def get_comments_count(self, obj):
        """Return the number of comments of the task."""
        return obj.comments.count()


class TaskUpdateSerializer(TaskPeopleSerializer):
    """Task update; the board of a task cannot be changed."""

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "status",
            "priority",
            "assignee",
            "reviewer",
            "assignee_id",
            "reviewer_id",
            "due_date",
        ]

    def validate(self, attrs):
        """Reject a different board, then check the people."""
        board = self.initial_data.get("board")
        if board is not None and str(board) != str(self.instance.board_id):
            raise serializers.ValidationError(
                {"board": "The board of a task cannot be changed."}
            )
        return super().validate(attrs)


class CommentSerializer(serializers.ModelSerializer):
    """Comment with the full name of its author."""

    author = serializers.CharField(source="author.first_name", read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "created_at", "author", "content"]
