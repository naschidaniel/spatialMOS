from rest_framework import serializers
from predictions.models import SpatialMosPoint, SpatialMosRun, SpatialMosStep

# Serializers define the API representation.
class SpatialMosStepSerializer(serializers.ModelSerializer):
    parameter = serializers.StringRelatedField(source='spatialmos_run.parameter')
    anal_date = serializers.DateTimeField(source='spatialmos_run.anal_date', format='%Y-%m-%d')
    valid_date = serializers.DateTimeField(format='%Y-%m-%d')
    valid_time = serializers.DateTimeField(source='valid_date', format='%H:%M')

    class Meta:
        model = SpatialMosStep
        fields = ['step', 'parameter', 'anal_date', 'valid_date', 'valid_time', 'filename_nwp_mean', 'filename_nwp_spread', 'filename_spatialmos_mean', 'filename_spatialmos_spread']


class SpatialMosRunSerializer(serializers.ModelSerializer):
    anal_date = serializers.DateTimeField(format='%Y-%m-%d')
    parameter_longname = serializers.SerializerMethodField()
    steps = SpatialMosStepSerializer(many=True, read_only=True)

    class Meta:
        model = SpatialMosRun
        fields = ['parameter', 'parameter_longname', 'anal_date', 'parameter', 'complete', 'steps']

    def get_parameter_longname(self, obj):
        return obj.get_parameter_display()


class SpatialMosPointSerializer(serializers.ModelSerializer):
    parameter = serializers.StringRelatedField(source='spatialmos_step.spaspatialmos_run.parameter')
    step = serializers.IntegerField(source='spatialmos_step.step')
    anal_date = serializers.DateTimeField(source='spatialmos_step.spatialmos_run.anal_date', format='%Y-%m-%d')
    valid_date = serializers.DateTimeField(source='spatialmos_step.valid_date', format='%Y-%m-%d')
    valid_time = serializers.DateTimeField(source='spatialmos_step.valid_date', format='%H:%M')

    class Meta:
        model = SpatialMosPoint
        fields = ['parameter', 'anal_date', 'valid_date', 'valid_time', 'step', 'lat', 'lon', 'samos_mean', 'samos_spread']

