from rest_framework import serializers
from assessments.models import Question


class QuestionSerializer(serializers.ModelSerializer):
    """Basic Question serializer"""
    assessment_id = serializers.PrimaryKeyRelatedField(
        queryset=None,  # Will be set in __init__
        source='assessment',
        write_only=True
    )
    assessment_display = serializers.CharField(source='assessment.__str__', read_only=True)
    clo_ids = serializers.PrimaryKeyRelatedField(
        queryset=None,  # Will be set in __init__
        source='clo',
        many=True,
        write_only=True
    )
    clos = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = [
            'id',
            'assessment_id',
            'assessment_display',
            'marks',
            'clo_ids',
            'clos',
        ]
        read_only_fields = ['id']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from assessments.models import Assessment
        from outcomes.models import CourseLearningOutcome
        self.fields['assessment_id'].queryset = Assessment.objects.all()
        self.fields['clo_ids'].queryset = CourseLearningOutcome.objects.all()

    def get_clos(self, obj):
        from outcomes.serializers import CLOSerializer
        return CLOSerializer(obj.clo.all(), many=True).data


class QuestionDetailSerializer(serializers.ModelSerializer):
    """Detailed Question serializer with student scores"""
    assessment_display = serializers.CharField(source='assessment.__str__', read_only=True)
    clos = serializers.SerializerMethodField()
    scores_count = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = [
            'id',
            'assessment_display',
            'marks',
            'clos',
            'scores_count',
        ]
        read_only_fields = ['id']

    def get_clos(self, obj):
        from outcomes.serializers import CLOSerializer
        return CLOSerializer(obj.clo.all(), many=True).data

    def get_scores_count(self, obj):
        return obj.student_scores.count()