from django.db import models
from django.utils import timezone

class Pages(models.Model):
    slug = models.SlugField(max_length=100, unique=True, primary_key=True)
    title = models.CharField(max_length=100)
    content = models.TextField()
    datePosted = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title']
