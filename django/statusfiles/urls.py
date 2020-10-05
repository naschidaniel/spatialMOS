"""The URL configuration file for the statusfiles app"""

from django.urls import path
from statusfiles import views

# statusfiles urls
urlpatterns = [
    path('', views.systemhealth, name='systemhealth'),
]