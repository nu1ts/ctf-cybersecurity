"""
URL configuration for todo_api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.shortcuts import redirect
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from api.serializers import RegisterView
from api.views import TaskListCreateAPIView, TaskDetailUpdateDeleteAPIView, TaskCompleteAPIView, \
    TaskUncompleteAPIView


def redirect_to_docs(request):
    return redirect('/api/swagger/')

urlpatterns = [
    path('', redirect_to_docs),
    path('admin/', admin.site.urls),
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/tasks/', TaskListCreateAPIView.as_view(), name='task-list-create'),
    path('api/tasks/<int:pk>/', TaskDetailUpdateDeleteAPIView.as_view(), name='task-detail-update-delete'),
    path('api/tasks/<int:pk>/complete/', TaskCompleteAPIView.as_view(), name='task-complete'),
    path('api/tasks/<int:pk>/uncomplete/', TaskUncompleteAPIView.as_view(), name='task-uncomplete'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger'),
]
