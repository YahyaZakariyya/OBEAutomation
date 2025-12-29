from rest_framework import serializers
from assessments.models import AssessmentBreakdown


class AssessmentBreakdownSerializer(serializers.ModelSerializer):
    """Assessment Breakdown serializer"""
    section_id = serializers.PrimaryKeyRelatedField(
        queryset=None,  # Will be set in __init__
        source='section',
        write_only=True
    )
    section_display = serializers.CharField(source='section.__str__', read_only=True)
    assessment_types = serializers.SerializerMethodField()

    class Meta:
        model = AssessmentBreakdown
        fields = [
            'id',
            'section_id',
            'section_display',
            'assignment_weightage',
            'quiz_weightage',
            'lab_weightage',
            'mid_weightage',
            'final_weightage',
            'project_weightage',
            'assessment_types',
        ]
        read_only_fields = ['id']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from sections.models import Section
        self.fields['section_id'].queryset = Section.objects.all()

    def get_assessment_types(self, obj):
        return obj.get_assessment_types()
