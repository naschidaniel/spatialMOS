from rest_framework import serializers
from predictions.models import SpatialMosRun

# Serializers define the API representation.
class SpatialMosRunSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = SpatialMosRun
        fields = ['parameter', 'anal_date', 'parameter', 'complete']
