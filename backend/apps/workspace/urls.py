from rest_framework.routers import DefaultRouter

from .views import NoteViewSet, TodoViewSet

router = DefaultRouter()
router.register('notes', NoteViewSet, basename='note')
router.register('todos', TodoViewSet, basename='todo')

urlpatterns = router.urls
