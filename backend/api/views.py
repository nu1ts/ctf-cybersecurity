from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Task
from .serializers import TaskSerializer, CustomTokenObtainPairSerializer


class TaskListCreateAPIView(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'priority']
    ordering_fields = ['deadline', 'created_at', 'id']
    ordering = ['deadline']
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

class TaskDetailUpdateDeleteAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    lookup_field = 'pk'
    permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        task = serializer.save()
        task.update_status()
        task.save()

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

class TaskCompleteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            task = Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            return Response({"detail": "404 Not Found"}, status=status.HTTP_404_NOT_FOUND)

        now = timezone.now().date()
        if task.deadline and now > task.deadline:
            task.status = 'Late'
        else:
            task.status = 'Completed'

        task.save()
        return Response(status=status.HTTP_200_OK)

class TaskUncompleteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            task = Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            return Response({"detail": "404 Not Found"}, status=status.HTTP_404_NOT_FOUND)

        now = timezone.now().date()
        if task.deadline and now > task.deadline:
            task.status = 'Overdue'
        else:
            task.status = 'Active'

        task.save()
        return Response(status=status.HTTP_200_OK)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer