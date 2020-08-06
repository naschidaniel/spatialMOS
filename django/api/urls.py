from django.urls import path, include

from . import views


# Wire up our API using automatic URL routing.
urlpatterns = [
    path('spatailmosrun/', views.SpatialMosRunList.as_view()),
    path('spatailmosrun/<int:pk>', views.SpatialMosRunDetails.as_view()),
    path('spatialmosrun/last/<parameter>/', views.SpatialMosRunLastDetails.as_view()),
    path('spatialmosstep/last/<parameter>/', views.SpatialMosLastRunSteps.as_view()),
    path('spatialmospoint/last/<parameter>/<lat>/<lon>/', views.SpatialMosLastRunPointPrediction.as_view()),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
