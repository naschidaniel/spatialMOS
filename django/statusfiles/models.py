"""The models for statusfiles are listed here."""

from django.db import models
from django.utils import timezone


class StatusFiles(models.Model):
    """The model for a listing all statusfiles"""
    taskname = models.CharField(max_length=500)
    task_finished_time = models.DateTimeField()
    cmd = models.CharField(max_length=500)
    dateImported = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        """Return Value in the Admin Panel"""
        return f"{self.task_finished_time.strftime('%Y-%m-%d %H:%M:%S')} | {self.taskname} | {self.cmd}"

    class Meta:
        """Settings"""
        ordering = ['task_finished_time', 'taskname', 'cmd']