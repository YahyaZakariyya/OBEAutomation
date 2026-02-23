from rest_framework import serializers
from assessments.models import Question


class QuestionSerializer(serializers.ModelSerializer):
    clo = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'assessment', 'marks', 'clo']


class QuestionWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'assessment', 'marks', 'clo']
