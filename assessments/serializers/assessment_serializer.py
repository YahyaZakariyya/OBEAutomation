from rest_framework import serializers
from assessments.models import Assessment, Question


class AssessmentQuestionSerializer(serializers.ModelSerializer):
    clo = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'marks', 'clo']


class AssessmentSerializer(serializers.ModelSerializer):
    questions = AssessmentQuestionSerializer(many=True, read_only=True)
    total_marks = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Assessment
        fields = ['id', 'title', 'section', 'date', 'type', 'weightage', 'questions', 'total_marks']

    def get_total_marks(self, obj):
        return obj.get_total_marks()
