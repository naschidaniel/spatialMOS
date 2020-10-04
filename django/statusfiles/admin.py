"""The models witch are displayed in the Admin Panel"""

from django.contrib import admin
from .models import StatusChecks, StatusFiles

# Registered models for the Admin panel
admin.site.register(StatusChecks)
admin.site.register(StatusFiles)
