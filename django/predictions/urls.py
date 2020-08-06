from django.urls import path

from . import views

urlpatterns = [
    path('', views.predictions, name='predictions'),
    path('punktvorhersagen/', views.pointpredictions, name='pointpredictions'),
]