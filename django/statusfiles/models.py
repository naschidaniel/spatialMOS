"""The models for statusfiles are listed here."""

from django.db import models
from django.utils import timezone


class StatusChecks(models.Model):
    """The model for sorting statusfiles into statuschecks"""
    available_max_age = (
        (70, "Stündlich"),
        (1460, "Täglich"),
        (10100, "Wöchentlich"),
    )
    taskname = models.CharField(max_length=500)
    cmd_regex = models.CharField(max_length=500)
    name = models.CharField(max_length=100)
    date_created = models.DateTimeField(default=timezone.now)
    max_age = models.IntegerField(default=70, choices=available_max_age)
    verified_by_admin = models.BooleanField(default=False)
    
    def __str__(self):
        """Return Value in the Admin Panel"""
        return f"{self.max_age} | {self.verified_by_admin} | {self.name}"

    class Meta:
        """Settings"""
        ordering = ['name', 'taskname', 'cmd_regex']


class StatusFiles(models.Model):
    """The model for a listing all statusfiles"""
    check_name = models.ForeignKey(StatusChecks, related_name="statuscheck", on_delete=models.CASCADE)
    task_finished_time = models.DateTimeField()
    cmd = models.CharField(max_length=500)
    date_imported = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        """Return Value in the Admin Panel"""
        return f"{self.task_finished_time.strftime('%Y-%m-%d %H:%M:%S')} | {self.check_name} | {self.cmd}"

    class Meta:
        """Settings"""
        ordering = ['task_finished_time', 'check_name', 'cmd']
        get_latest_by = "task_finished_time"
