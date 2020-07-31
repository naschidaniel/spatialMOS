from django.urls import path

from . import views

urlpatterns = [
    path('', views.predictions, name='predictions'),
]