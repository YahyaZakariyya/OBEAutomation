from rest_framework import serializers
from .models import Question, StudentQuestionScore, CustomUser

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'marks']

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'first_name', 'last_name']

class StudentQuestionScoreSerializer(serializers.ModelSerializer):
    student_id = serializers.IntegerField(source='student.id')
    question_id = serializers.IntegerField(source='question.id')

    class Meta:
        model = StudentQuestionScore
        fields = ['student_id', 'question_id', 'marks_obtained']
