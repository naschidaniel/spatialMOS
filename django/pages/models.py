"""The models for Pages are listed here."""

from django.db import models
from django.utils import timezone

class Pages(models.Model):
    """The model is responsible for the return of static pages."""
    slug = models.SlugField(max_length=100, unique=True, primary_key=True)
    title = models.CharField(max_length=100)
    content = models.TextField()
    datePosted = models.DateTimeField(default=timezone.now)

    def __str__(self):
        """Return Value in the Admin Panel"""
        return self.title

    class Meta:
        """Settings for Pages in the Admin Panel"""
        ordering = ['title']
