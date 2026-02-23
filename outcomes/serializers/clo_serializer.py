from rest_framework import serializers
from outcomes.models import CourseLearningOutcome


class CLOSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseLearningOutcome
        fields = ['id', 'course', 'CLO', 'heading', 'description', 'weightage']
