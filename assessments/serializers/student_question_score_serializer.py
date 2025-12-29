from rest_framework import serializers
from assessments.models import StudentQuestionScore
from users.serializers import CustomUserSerializer


class StudentQuestionScoreSerializer(serializers.ModelSerializer):
    """Basic Student Question Score serializer"""
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=None,  # Will be set in __init__
        source='student',
        write_only=True
    )
    question_id = serializers.PrimaryKeyRelatedField(
        queryset=None,  # Will be set in __init__
        source='question',
        write_only=True
    )
    student = CustomUserSerializer(read_only=True)
    question_marks = serializers.FloatField(source='question.marks', read_only=True)

    class Meta:
        model = StudentQuestionScore
        fields = [
            'id',
            'student',
            'student_id',
            'question_id',
            'question_marks',
            'marks_obtained',
        ]
        read_only_fields = ['id']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from users.models import CustomUser
        from assessments.models import Question
        self.fields['student_id'].queryset = CustomUser.objects.filter(role='student')
        self.fields['question_id'].queryset = Question.objects.all()


class StudentQuestionScoreDetailSerializer(serializers.ModelSerializer):
    """Detailed Student Question Score serializer"""
    student = CustomUserSerializer(read_only=True)
    question_display = serializers.CharField(source='question.__str__', read_only=True)
    question_marks = serializers.FloatField(source='question.marks', read_only=True)
    percentage = serializers.SerializerMethodField()

    class Meta:
        model = StudentQuestionScore
        fields = [
            'id',
            'student',
            'question_display',
            'question_marks',
            'marks_obtained',
            'percentage',
        ]
        read_only_fields = ['id']

    def get_percentage(self, obj):
        if obj.question.marks > 0:
            return (obj.marks_obtained / obj.question.marks) * 100
        return 0