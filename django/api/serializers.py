from rest_framework import serializers
from predictions.models import SpatialMosRun, SpatialMosStep

# Serializers define the API representation.
class SpatialMosRunSerializer(serializers.ModelSerializer):
    anal_date = serializers.DateTimeField(format='%Y-%m-%d', input_formats=None)

    class Meta:
        model = SpatialMosRun
        fields = ['id', 'parameter', 'anal_date', 'parameter', 'complete']

class SpatialMosStepSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = SpatialMosStep
        fields = ['spatialmos_run', 'spatialmos_run', 'valid_date', 'step']