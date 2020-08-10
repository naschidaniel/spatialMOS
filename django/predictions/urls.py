"""The URL configuration file for the predictions app"""

from django.urls import path
from predictions import views

# predictions urls
urlpatterns = [
    path('', views.predictions, name='predictions'),
    path('punktvorhersagen/', views.pointpredictions, name='pointpredictions'),
]