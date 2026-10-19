"""URL routes of the kanban app."""
from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import BoardViewSet, TaskCommentViewSet, TaskViewSet

router = SimpleRouter()
router.register("boards", BoardViewSet, basename="board")
router.register("tasks", TaskViewSet, basename="task")

comment_list = TaskCommentViewSet.as_view({"get": "list", "post": "create"})
comment_detail = TaskCommentViewSet.as_view({"delete": "destroy"})

urlpatterns = [
    path("tasks/<int:task_id>/comments/", comment_list, name="task-comments"),
    path(
        "tasks/<int:task_id>/comments/<int:pk>/",
        comment_detail,
        name="task-comment-detail",
    ),
] + router.urls
