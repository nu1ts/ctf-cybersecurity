import datetime
import pytest
from django.utils import timezone
from api.models import Task

@pytest.mark.django_db
class TestTaskMacroParsing:
    @pytest.mark.parametrize("title,expected_priority", [
        ("!1 Urgent task", "Critical"),
        ("!2 Important task", "High"),
        ("!3 Normal task", "Medium"),
        ("!4 Minor task", "Low"),
        ("!0 Wrong macro", "Medium"),
        ("!5 Wrong macro", "Medium"),
        ("No macro", "Medium"),
    ])
    def test_priority_macro_parsing(self, title, expected_priority):
        """
        Проверяет, что макросы !1–!4 корректно преобразуются в приоритеты задачи,
        а макросы удаляются из заголовка задачи.
        Также проверяет, что при отсутствии макроса приоритет по умолчанию "Medium".
        """
        task = Task.objects.create(title=title)
        assert task.priority == expected_priority
        assert "!1" not in task.title
        assert "!2" not in task.title
        assert "!3" not in task.title
        assert "!4" not in task.title

    @pytest.mark.parametrize("title,expected_date", [
        ("!before 15.02.2024 Deadline task", datetime.date(2024, 2, 15)),
        ("!before 05-01-2025 Another task", datetime.date(2025, 1, 5)),
        ("!before 31-12-2023 Final task", datetime.date(2023, 12, 31)),
    ])
    def test_deadline_macro_parsing_valid(self, title, expected_date):
        """
        Проверяет корректный парсинг макроса !before с разными форматами даты,
        и что макрос удаляется из заголовка.
        """
        task = Task.objects.create(title=title)
        assert task.deadline == expected_date
        assert "!before" not in task.title

    @pytest.mark.parametrize("title", [
        "!before 32.01.2024",
        "!before 15.13.2024",
        "!before ab.cd.efgh",
    ])
    def test_deadline_macro_parsing_invalid(self, title):
        """
        Проверяет, что при неверных датах в макросе !before дедлайн не устанавливается (None).
        """
        task = Task.objects.create(title=title)
        assert task.deadline is None

    def test_manual_priority_overrides_macro(self):
        """
        Проверяет, что если приоритет задан вручную, он не перезаписывается макросом в заголовке.
        """
        task = Task.objects.create(title="!1 Critical by macro", priority="Low")
        assert task.priority == "Low"

    def test_manual_deadline_overrides_macro(self):
        """
        Проверяет, что если дедлайн задан вручную, он не перезаписывается макросом в заголовке.
        """
        manual_deadline = datetime.date(2025, 5, 21)
        task = Task.objects.create(title="!before 15.02.2024 Task", deadline=manual_deadline)
        assert task.deadline == manual_deadline

    def test_title_cleaned_of_macros(self):
        """
        Проверяет, что после создания задачи из заголовка удаляются все макросы,
        а остальной текст сохраняется.
        """
        task = Task.objects.create(title="!1 !before 15.02.2024 Clean title")
        assert "!1" not in task.title
        assert "!before" not in task.title
        assert "Clean title" in task.title

@pytest.mark.django_db
class TestTaskStatusTransitions:
    def test_status_becomes_overdue_if_deadline_passed(self):
        """
        Проверяет, что если дедлайн задачи прошёл, статус автоматически меняется на "Overdue".
        """
        past_deadline = timezone.now().date() - datetime.timedelta(days=1)
        task = Task.objects.create(title="Test", deadline=past_deadline)
        assert task.status == "Overdue"

    def test_status_stays_active_if_deadline_in_future(self):
        """
        Проверяет, что если дедлайн в будущем, статус задачи остаётся "Active".
        """
        future_deadline = timezone.now().date() + datetime.timedelta(days=5)
        task = Task.objects.create(title="Test", deadline=future_deadline)
        assert task.status == "Active"

    def test_completed_to_late_if_deadline_passed(self):
        """
        Проверяет, что если задача со статусом "Completed" имеет просроченный дедлайн,
        статус меняется на "Late".
        """
        past_deadline = timezone.now().date() - datetime.timedelta(days=1)
        task = Task.objects.create(title="Done", deadline=past_deadline, status="Completed")
        task.save()
        assert task.status == "Late"

    def test_late_to_completed_if_deadline_extended(self):
        """
        Проверяет, что если статус "Late", но дедлайн продлён на будущее,
        статус меняется обратно на "Completed".
        """
        future_deadline = timezone.now().date() + datetime.timedelta(days=5)
        task = Task.objects.create(title="Late one", deadline=timezone.now().date() - datetime.timedelta(days=1), status="Late")
        task.deadline = future_deadline
        task.save()
        assert task.status == "Completed"