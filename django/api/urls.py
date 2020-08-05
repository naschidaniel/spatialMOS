from django.urls import path, include

from api.views import SpatialMosRunDetails
from . import views


# ViewSets define the view behavior.


# Wire up our API using automatic URL routing.
urlpatterns = [
    path('spatailmosrun/', views.SpatialMosRunList.as_view()),
    path('spatailmosrun/<int:pk>', views.SpatialMosRunDetails.as_view()),
    path('spatialmosrun/last/<parameter>/', views.SpatialMosRunLastDetails.as_view()),
    path('spatialmosstep/last/<parameter>/', views.SpatialMosRunLastStepDetails.as_view()),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
