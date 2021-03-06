"""The Serializers for spatialMOS"""

from rest_framework import serializers
from predictions.models import SpatialMosPoint, SpatialMosRun, SpatialMosStep


# Serializers
class SpatialMosStepSerializer(serializers.ModelSerializer):
    """Serializer for the spatialmos steps"""
    parameter = serializers.StringRelatedField(source='spatialmos_run.parameter')
    unit = serializers.StringRelatedField(source='spatialmos_run.unit')
    anal_date = serializers.DateTimeField(source='spatialmos_run.anal_date', format='%Y-%m-%d')
    valid_date = serializers.DateTimeField(format='%Y-%m-%d')
    valid_time = serializers.DateTimeField(source='valid_date', format='%H:%M')

    class Meta:
        """Return values"""
        model = SpatialMosStep
        fields = ['step', 'parameter', 'unit', 'anal_date', 'valid_date', 'valid_time', \
            'filename_nwp_mean_sm', 'filename_nwp_mean_md', 'filename_nwp_mean_lg', \
            'filename_nwp_spread_sm', 'filename_nwp_spread_md', 'filename_nwp_spread_lg', \
            'filename_spatialmos_mean_sm', 'filename_spatialmos_mean_md', 'filename_spatialmos_mean_lg', \
            'filename_spatialmos_spread_sm', 'filename_spatialmos_spread_md', 'filename_spatialmos_spread_lg' \
            ]


class SpatialMosRunSerializer(serializers.ModelSerializer):
    """Serializer for the spatialmos model runs"""
    anal_date = serializers.DateTimeField(format='%Y-%m-%d')
    parameter_longname = serializers.SerializerMethodField()
    steps = SpatialMosStepSerializer(many=True, read_only=True)

    class Meta:
        """Return values"""
        model = SpatialMosRun
        fields = ['parameter', 'parameter_longname', 'anal_date', 'parameter', 'complete', 'steps']

    def get_parameter_longname(self, obj):
        """A function to determine the name from the selection menu"""
        return obj.get_parameter_display()


class SpatialMosPointSerializer(serializers.ModelSerializer):
    """Serializer for the spatialmos points"""
    parameter = serializers.StringRelatedField(source='spatialmos_step.spatialmos_run.parameter')
    unit = serializers.StringRelatedField(source='spatialmos_step.spatialmos_run.unit')
    step = serializers.IntegerField(source='spatialmos_step.step')
    anal_date = serializers.DateTimeField(source='spatialmos_step.spatialmos_run.anal_date', format='%Y-%m-%d')
    valid_date = serializers.DateTimeField(source='spatialmos_step.valid_date', format='%Y-%m-%d')
    valid_time = serializers.DateTimeField(source='spatialmos_step.valid_date', format='%H:%M')

    class Meta:
        """Return values"""
        model = SpatialMosPoint
        fields = ['parameter', 'anal_date', 'valid_date', 'valid_time', 'step', 'lat', 'lon', 'unit', 'spatialmos_mean', 'spatialmos_spread']
