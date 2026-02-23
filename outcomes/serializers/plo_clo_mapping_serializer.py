from rest_framework import serializers
from outcomes.models import PloCloMapping


class PloCloMappingSerializer(serializers.ModelSerializer):
    plo_heading = serializers.CharField(source='plo.heading', read_only=True)
    clo_heading = serializers.CharField(source='clo.heading', read_only=True)

    class Meta:
        model = PloCloMapping
        fields = ['id', 'program', 'course', 'plo', 'clo', 'weightage', 'plo_heading', 'clo_heading']
