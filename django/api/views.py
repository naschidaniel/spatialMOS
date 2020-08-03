from rest_framework import viewsets
from predictions.models import SpatialMosRun
from .serializers import SpatialMosRunSerializer

class SpatialMosRunViewSet(viewsets.ModelViewSet):
    queryset = SpatialMosRun.objects.all()
    serializer_class = SpatialMosRunSerializer
