from predictions.models import SpatialMosRun, SpatialMosStep, SpatialMosPoint
from .serializers import SpatialMosRunSerializer, SpatialMosStepSerializer, SpatialMosPointSerializer
from django.http import Http404, JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status


class SpatialMosRunList(APIView):  
    """List all SpatialMosRuns."""

    permission_classes = [AllowAny]
    def get(self, request, format=None):
        spatialmos_runs = SpatialMosRun.objects.all()
        serializer = SpatialMosRunSerializer(spatialmos_runs, context={'request': request}, many=True)
        return JsonResponse(serializer.data, safe=False)

class SpatialMosRunDetails(APIView):  
    """List details for one SpatialMosRun."""

    permission_classes = [AllowAny]
    def get_object(self, pk):
        try:
            return SpatialMosRun.objects.get(pk=pk)
        except SpatialMosRun.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        spatialmos_run = self.get_object(pk)
        serializer = SpatialMosRunSerializer(spatialmos_run, context={'request': request})
        return JsonResponse(serializer.data, safe=False)

class SpatialMosRunLastDetails(APIView):  
    """List details for last SpatialMosRun."""

    permission_classes = [AllowAny]
    def get_object(self, parameter):
        try:
            return SpatialMosRun.objects.filter(parameter=parameter).latest('anal_date')
        except SpatialMosRun.DoesNotExist:
            raise Http404

    def get(self, request, parameter, format=None):
        spatialmos_run = self.get_object(parameter)
        serializer = SpatialMosRunSerializer(spatialmos_run, context={'request': request})
        return JsonResponse(serializer.data, safe=False)

class SpatialMosLastRunSteps(APIView):  
    """List details of all steps for last SpatialMosRun."""
    permission_classes = [AllowAny]
    def get_object(self, parameter):
        try:
            spatialmos_run = SpatialMosRun.objects.filter(parameter=parameter).latest('anal_date')
            return spatialmos_run.steps.all()
        except SpatialMosStep.DoesNotExist:
            raise Http404

    def get(self, request, parameter, format=None):
        spatialmos_steps = self.get_object(parameter)
        serializer = SpatialMosStepSerializer(spatialmos_steps, context={'request': request}, many=True)
        return JsonResponse(serializer.data, safe=False)

class SpatialMosLastRunPointPrediction(APIView):  
    """List predictions for a point from the the last SpatialMosRun."""
    permission_classes = [AllowAny]
    def get_object(self, parameter, lat, lon):
        try:
            lat = float(lat)
            lon = float(lon)
            lat_gridsize = 0.0083582089 / 2
            lon_gridsize = 0.0083421330 / 2
            min_lat = lat - lat_gridsize
            max_lat = lat + lat_gridsize
            min_lon = lon - lon_gridsize
            max_lon = lon + lon_gridsize

            spatialmos_run = SpatialMosRun.objects.filter(parameter=parameter).latest('anal_date')
            return SpatialMosPoint.objects.filter(spatialmos_step__spatialmos_run=spatialmos_run, lat__range=[min_lat, max_lat], lon__range=[min_lon, max_lon])
        except SpatialMosStep.DoesNotExist:
            raise Http404

    def get(self, request, parameter, lat, lon, format=None):
        spatialmos_steps = self.get_object(parameter, lat, lon)
        serializer = SpatialMosPointSerializer(spatialmos_steps, many=True)
        return JsonResponse(serializer.data, safe=False)