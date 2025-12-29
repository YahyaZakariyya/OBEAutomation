from rest_framework import serializers
from assessments.models import Assessment


class AssessmentSerializer(serializers.ModelSerializer):
    """Basic Assessment serializer"""
    section_id = serializers.PrimaryKeyRelatedField(
        queryset=None,  # Will be set in __init__
        source='section',
        write_only=True
    )
    section_display = serializers.CharField(source='section.__str__', read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    total_marks = serializers.SerializerMethodField()

    class Meta:
        model = Assessment
        fields = [
            'id',
            'title',
            'section_id',
            'section_display',
            'date',
            'type',
            'type_display',
            'weightage',
            'total_marks',
        ]
        read_only_fields = ['id']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from sections.models import Section
        self.fields['section_id'].queryset = Section.objects.all()

    def get_total_marks(self, obj):
        return obj.get_total_marks()


class AssessmentDetailSerializer(serializers.ModelSerializer):
    """Detailed Assessment serializer with questions"""
    section_display = serializers.CharField(source='section.__str__', read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    total_marks = serializers.SerializerMethodField()
    questions_count = serializers.SerializerMethodField()

    class Meta:
        model = Assessment
        fields = [
            'id',
            'title',
            'section_display',
            'date',
            'type',
            'type_display',
            'weightage',
            'total_marks',
            'questions_count',
        ]
        read_only_fields = ['id']

    def get_total_marks(self, obj):
        return obj.get_total_marks()

    def get_questions_count(self, obj):
        return obj.questions.count()
