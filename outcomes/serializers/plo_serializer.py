from rest_framework import serializers
from outcomes.models import ProgramLearningOutcome

class PLOSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramLearningOutcome
        fields = ['id', 'PLO', 'heading']