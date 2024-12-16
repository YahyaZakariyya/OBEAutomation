from rest_framework import serializers
from assessments.models import StudentQuestionScore

class StudentQuestionScoreSerializer(serializers.ModelSerializer):
    student_id = serializers.IntegerField(source='student.id')
    question_id = serializers.IntegerField(source='question.id')

    class Meta:
        model = StudentQuestionScore
        fields = ['student_id', 'question_id', 'marks_obtained']