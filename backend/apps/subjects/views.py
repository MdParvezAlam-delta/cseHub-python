from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Subject
from .serializers import SubjectSerializer


import logging

logger = logging.getLogger(__name__)

class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_active=True)
        return queryset

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
