from rest_framework import viewsets
from predictions.models import SpatialMosRun, SpatialMosStep
from .serializers import SpatialMosRunSerializer, SpatialMosStepSerializer

class SpatialMosRunViewSet(viewsets.ModelViewSet):
    queryset = SpatialMosRun.objects.all()
    serializer_class = SpatialMosRunSerializer

class SpatialMosStepViewSet(viewsets.ModelViewSet):
    queryset = SpatialMosStep.objects.all()
    serializer_class = SpatialMosStepSerializer
