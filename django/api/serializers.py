from rest_framework import serializers
from predictions.models import SpatialMosRun, SpatialMosStep

# Serializers define the API representation.
class SpatialMosRunSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = SpatialMosRun
        fields = ['parameter', 'anal_date', 'parameter', 'complete']

class SpatialMosStepSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = SpatialMosStep
        fields = ['spatialmos_run', 'spatialmos_run', 'valid_date', 'step']