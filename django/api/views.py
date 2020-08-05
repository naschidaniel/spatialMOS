from predictions.models import SpatialMosRun
from .serializers import SpatialMosRunSerializer
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status


class SpatialMosRunList(APIView):  
    permission_classes = [AllowAny]
    """
    List all snippets, or create a new snippet.
    """
    def get(self, request, format=None):
        spatialmos_run = SpatialMosRun.objects.all()
        serializer = SpatialMosRunSerializer(spatialmos_run, many=True)
        return Response(serializer.data)

class SpatialMosRunDetails(APIView):  
    permission_classes = [AllowAny]
    """
    List all snippets, or create a new snippet.
    """
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
    permission_classes = [AllowAny]
    """
    List all snippets, or create a new snippet.
    """
    print("SpatialMosRunLastDetails")
    def get_object(self, parameter):
        print("ajdkfjaöfjajdöl")
        try:
            return SpatialMosRun.objects.latest(parameter=parameter)
        except SpatialMosRun.DoesNotExist:
            raise Http404

    def get(self, request, parameter, format=None):
        print(parameter)

        spatialmos_run = SpatialMosRun.objects.filter(parameter=parameter).latest('anal_date')
        serializer = SpatialMosRunSerializer(spatialmos_run)
        return Response(serializer.data)
