from rest_framework import serializers
from predictions.models import SpatialMosRun, SpatialMosStep

# Serializers define the API representation.
class SpatialMosRunSerializer(serializers.ModelSerializer):
    anal_date = serializers.DateTimeField(format='%Y-%m-%d', input_formats=None)

    class Meta:
        model = SpatialMosRun
        fields = ['id', 'parameter', 'anal_date', 'parameter', 'complete']

class SpatialMosStepSerializer(serializers.ModelSerializer):
    parameter = serializers.StringRelatedField(source='spatialmos_run.parameter')
    anal_date = serializers.DateTimeField(source='spatialmos_run.anal_date', format='%Y-%m-%d', input_formats=None)
    valid_date = serializers.DateTimeField(format='%Y-%m-%d', input_formats=None)

    class Meta:
        model = SpatialMosStep
        fields = ['id', 'anal_date', 'valid_date', 'step', 'parameter', 'filename_nwp_mean', 'filename_nwp_spread', 'filename_spatialmos_mean', 'filename_spatialmos_spread']
