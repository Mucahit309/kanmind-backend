"""URL routes of the kanban app."""
from rest_framework.routers import SimpleRouter

from .views import BoardViewSet

router = SimpleRouter()
router.register("boards", BoardViewSet, basename="board")

urlpatterns = router.urls
