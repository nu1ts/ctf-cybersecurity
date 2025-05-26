from django.contrib.auth.models import User
from rest_framework import serializers, generics
from rest_framework.permissions import AllowAny
from rest_framework.serializers import ModelSerializer
from .models import Task

class TaskSerializer(serializers.ModelSerializer):
    title = serializers.CharField(min_length=4)

    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ['status', 'created_at', 'updated_at', 'user']

    def create(self, validated_data):
        task = Task(**validated_data)

        task.save()

        return task

class UserRegisterSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserRegisterSerializer