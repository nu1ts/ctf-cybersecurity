import os
import django
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'todo_api.settings')
django.setup()

from django.contrib.auth.models import User
from api.models import Task

def create_admin_with_flag():
    admin_user, created = User.objects.get_or_create(username='admin')
    if created:
        admin_user.set_password('adminpass')
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()

    flag = "HITS{jwt_and_idor_exploited_successfully}"
    existing_task = Task.objects.filter(user=admin_user, description__contains=flag).first()
    if existing_task:
        print("Флаг уже присутствует в базе.")
    else:
        task = Task.objects.create(
            user=admin_user,
            title="CTF Flag Task",
            description=flag,
            deadline=timezone.now().date(),
            priority='Critical',
            status='Active',
        )
        print(f"Задача с флагом создана: {task}")

def create_user_with_tasks(username, password, tasks_data):
    user, created = User.objects.get_or_create(username=username)
    if created:
        user.set_password(password)
        user.save()
        print(f"Пользователь создан: {username}")
    else:
        print(f"Пользователь уже существует: {username}")

    for task_info in tasks_data:
        exists = Task.objects.filter(user=user, title=task_info['title']).exists()
        if not exists:
            task = Task.objects.create(
                user=user,
                title=task_info['title'],
                description=task_info['description'],
                deadline=task_info.get('deadline', timezone.now().date()),
                priority=task_info.get('priority', 'Normal'),
                status=task_info.get('status', 'Active'),
            )
            print(f"Задача создана для {username}: {task.title}")

if __name__ == "__main__":
    create_admin_with_flag()

    create_user_with_tasks("nikita", "nikitapass", [
        {"title": "Nikita's Task 1", "description": "Task description 1", "priority": "High"},
        {"title": "Nikita's Task 2", "description": "Task description 2", "priority": "Low"},
    ])

    create_user_with_tasks("alice", "alicepass", [
        {"title": "Alice's Task 1", "description": "Alice's first task", "priority": "Medium"},
    ])

    create_user_with_tasks("bob", "bobpass", [
        {"title": "Bob's Task 1", "description": "Bob's important task", "priority": "Critical"},
        {"title": "Bob's Task 2", "description": "Bob's other task", "priority": "Normal"},
    ])