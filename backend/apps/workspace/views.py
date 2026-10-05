from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from .models import Note, Todo
from .serializers import NoteSerializer, TodoSerializer


class UserOwnedViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class NoteViewSet(UserOwnedViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer


class TodoViewSet(UserOwnedViewSet):
    queryset = Todo.objects.all()
    serializer_class = TodoSerializer
