import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.utils import timezone
from datetime import timedelta

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def create_task(api_client):
    """
    Фабрика создания задачи через API.
    Принимает словарь с параметрами задачи.
    """
    def _create_task(data):
        url = reverse('task-list-create')
        response = api_client.post(url, data, format='json')
        return response
    return _create_task


@pytest.mark.django_db
class TestTaskAPI:
    @pytest.mark.parametrize("title,expected_priority", [
        ("Test task !1", "Critical"),
        ("Test task !2", "High"),
        ("Test task !3", "Medium"),
        ("Test task !4", "Low"),
        ("Test task without macro", "Medium"),
    ])
    def test_create_task_priority_from_title_macro(self, api_client, create_task, title, expected_priority):
        """
        Проверяем, что при создании задачи с макросом приоритета в названии
        приоритет устанавливается корректно.
        """

        data = {"title": title, "description": "desc"}
        response = create_task(data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["priority"] == expected_priority
        assert not any(f"!{i}" in response.data["title"] for i in range(1, 5))

    @pytest.mark.parametrize("title,expected_deadline", [
        ("Task !before 15.05.2025", timezone.datetime(2025, 5, 15).date()),
        ("Task !before 01-01-2024", timezone.datetime(2024, 1, 1).date()),
        ("Task !before 31.12.2023", timezone.datetime(2023, 12, 31).date()),
    ])
    def test_create_task_deadline_from_title_macro(self, api_client, create_task, title, expected_deadline):
        """
        Проверяем, что при создании задачи с макросом дедлайна !before дата
        дедлайн парсится и устанавливается корректно.
        """
        data = {"title": title, "description": "desc"}
        response = create_task(data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["deadline"] == expected_deadline.isoformat()
        assert "!before" not in response.data["title"]

    @pytest.mark.parametrize("title,deadline,expected_status", [
        ("Active task", timezone.now().date() + timedelta(days=5), "Active"),
        ("Overdue task", timezone.now().date() - timedelta(days=1), "Overdue"),
        ("No deadline task", None, "Active"),
    ])
    def test_status_computation_on_create(self, api_client, create_task, title, deadline, expected_status):
        """
        Проверяем, что статус задачи рассчитывается корректно при создании,
        в зависимости от дедлайна и текущей даты.
        """
        data = {"title": title, "deadline": deadline.isoformat() if deadline else None}
        response = create_task(data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["status"] == expected_status

    def test_title_min_length_validation(self, api_client, create_task):
        """
        Проверяем валидацию минимальной длины названия задачи.
        """
        data = {"title": "abc"}
        response = create_task(data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "title" in response.data

    @pytest.mark.parametrize("priority_field,title_macro,expected_priority", [
        ("High", "Task !2", "High"),
        ("Medium", "Task !3", "Medium"),
        ("Low", "Task !4", "Low"),
    ])
    def test_priority_field_overrides_macro(self, api_client, create_task, priority_field, title_macro, expected_priority):
        """
        Приоритет из поля формы должен иметь приоритет над макросом в названии.
        """
        data = {"title": title_macro, "priority": priority_field}
        response = create_task(data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["priority"] == priority_field

    def test_update_task_and_status_transition(self, api_client, create_task):
        """
        Проверяем редактирование задачи и автоматический пересчёт статуса.
        """
        data = {"title": "Test update", "deadline": (timezone.now().date() + timedelta(days=5)).isoformat()}
        response = create_task(data)
        assert response.status_code == status.HTTP_201_CREATED
        task_id = response.data["id"]

        url = reverse('task-detail-update-delete', kwargs={'pk': task_id})
        update_data = {"deadline": (timezone.now().date() - timedelta(days=1)).isoformat()}
        response = api_client.patch(url, update_data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "Overdue"

    @pytest.mark.parametrize("initial_deadline,complete_date,expected_status", [
        (timezone.now().date() + timedelta(days=1), timezone.now().date(), "Completed"),
        (timezone.now().date() - timedelta(days=1), timezone.now().date(), "Late"),
    ])
    def test_mark_task_completed_status(self, api_client, create_task, initial_deadline, complete_date, expected_status):
        """
        Проверяем правильное обновление статуса задачи при отметке выполненной.
        """
        data = {"title": "Complete test", "deadline": initial_deadline.isoformat()}
        response = create_task(data)
        assert response.status_code == status.HTTP_201_CREATED
        task_id = response.data["id"]

        url = reverse('task-complete', kwargs={'pk': task_id})

        response = api_client.post(url)
        assert response.status_code == status.HTTP_200_OK

        detail_url = reverse('task-detail-update-delete', kwargs={'pk': task_id})
        task_resp = api_client.get(detail_url)
        assert task_resp.data["status"] == expected_status

    @pytest.mark.parametrize("initial_deadline,uncomplete_date,expected_status", [
        (timezone.now().date() + timedelta(days=1), timezone.now().date(), "Active"),
        (timezone.now().date() - timedelta(days=1), timezone.now().date(), "Overdue"),
    ])
    def test_mark_task_uncompleted_status(self, api_client, create_task, initial_deadline, uncomplete_date, expected_status):
        """
        Проверяем статус задачи при снятии отметки выполненной.
        """
        data = {"title": "Uncomplete test", "deadline": initial_deadline.isoformat()}
        response = create_task(data)
        assert response.status_code == status.HTTP_201_CREATED
        task_id = response.data["id"]

        complete_url = reverse('task-complete', kwargs={'pk': task_id})
        api_client.post(complete_url)

        uncomplete_url = reverse('task-uncomplete', kwargs={'pk': task_id})
        response = api_client.post(uncomplete_url)
        assert response.status_code == status.HTTP_200_OK

        detail_url = reverse('task-detail-update-delete', kwargs={'pk': task_id})
        task_resp = api_client.get(detail_url)
        assert task_resp.data["status"] == expected_status

    def test_delete_task(self, api_client, create_task):
        """
        Проверяем удаление задачи.
        """
        data = {"title": "Delete test"}
        response = create_task(data)
        task_id = response.data["id"]

        url = reverse('task-detail-update-delete', kwargs={'pk': task_id})
        del_resp = api_client.delete(url)
        assert del_resp.status_code == status.HTTP_204_NO_CONTENT

        get_resp = api_client.get(url)
        assert get_resp.status_code == status.HTTP_404_NOT_FOUND