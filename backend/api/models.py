from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
import re

class Task(models.Model):
    PRIORITY_CHOICES = (
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
        ('Critical', 'Critical'),
    )

    STATUS_CHOICES = (
        ('Active', 'Active'),
        ('Completed', 'Completed'),
        ('Overdue', 'Overdue'),
        ('Late', 'Late'),
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    deadline = models.DateField(null=True, blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='Medium')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')

    def update_status(self, old_deadline=None, old_status=None):
        today = timezone.now().date()

        if old_status == 'Late' and self.status == 'Late' and self.deadline and self.deadline >= today:
            self.status = 'Completed'
            return

        if old_status == 'Completed' and self.status == 'Completed' and self.deadline and self.deadline < today:
            self.status = 'Late'
            return

        if self.status not in ['Completed', 'Late']:
            if self.deadline:
                self.status = 'Overdue' if self.deadline < today else 'Active'
            else:
                self.status = 'Active'

    def save(self, *args, **kwargs):
        old_deadline = None
        old_status = None

        if self.pk:
            try:
                old_instance = Task.objects.get(pk=self.pk)
                old_deadline = old_instance.deadline
                old_status = old_instance.status
            except Task.DoesNotExist:
                pass

        if self.title:
            priority_match = re.search(r'!([1-4])', self.title)
            if priority_match and self.priority == 'Medium':
                priority_map = {
                    '1': 'Critical',
                    '2': 'High',
                    '3': 'Medium',
                    '4': 'Low',
                }
                self.priority = priority_map.get(priority_match.group(1), 'Medium')

            deadline_match = re.search(r'!before\s*([0-3]?\d)[.-]([0-1]?\d)[.-](\d{4})', self.title)
            if deadline_match and self.deadline == None:
                day = int(deadline_match.group(1))
                month = int(deadline_match.group(2))
                year = int(deadline_match.group(3))
                try:
                    self.deadline = timezone.datetime(year, month, day).date()
                except ValueError:
                    pass

            self.title = re.sub(r'!([1-4])', '', self.title)
            self.title = re.sub(r'!before\s*[0-3]?\d[.-][0-1]?\d[.-]\d{4}', '', self.title)
            self.title = self.title.strip()

        self.update_status(old_deadline=old_deadline, old_status=old_status)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title