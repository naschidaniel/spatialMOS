"""The URL configuration file for the predictions app"""

from django.urls import path
from predictions import views

# predictions urls
urlpatterns = [
    path('', views.predictions, name='predictions'),
    path('adresse/', views.addressprediction, name='addressprediction'),
    path('punktvorhersagen/', views.pointprediction, name='pointprediction'),
]