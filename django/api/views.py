from predictions.models import SpatialMosRun, SpatialMosStep
from .serializers import SpatialMosRunSerializer, SpatialMosStepSerializer
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status


class SpatialMosRunList(APIView):  
    """List all SpatialMosRuns."""

    permission_classes = [AllowAny]
    def get(self, request, format=None):
        spatialmos_runs = SpatialMosRun.objects.all()
        serializer = SpatialMosRunSerializer(spatialmos_runs, many=True)
        return Response(serializer.data)

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
        serializer = SpatialMosRunSerializer(spatialmos_run)
        return Response(serializer.data)

class SpatialMosRunLastDetails(APIView):  
    """List details for last SpatialMosRun."""

    permission_classes = [AllowAny]
    def get_object(self, parameter):
        try:
            return SpatialMosRun.objects.latest(parameter=parameter)
        except SpatialMosRun.DoesNotExist:
            raise Http404

    def get(self, request, parameter, format=None):
        spatialmos_run = SpatialMosRun.objects.filter(parameter=parameter).latest('anal_date')
        serializer = SpatialMosRunSerializer(spatialmos_run)
        return Response(serializer.data)

class SpatialMosRunLastStepDetails(APIView):  
    """List details of all steps for last SpatialMosRun."""
    permission_classes = [AllowAny]
    def get_object(self, parameter):
        try:
            return SpatialMosStep.objects.filter(spatialmos_run__parameter=parameter).latest('spatialmos_run__anal_date')
        except SpatialMosStep.DoesNotExist:
            raise Http404

    def get(self, request, parameter, format=None):
        spatialmos_steps = SpatialMosStep.objects.all()
        serializer = SpatialMosStepSerializer(spatialmos_steps, many=True)
        return Response(serializer.data)