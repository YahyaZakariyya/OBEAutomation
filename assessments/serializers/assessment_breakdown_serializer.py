from rest_framework import serializers
from assessments.models import AssessmentBreakdown


class AssessmentBreakdownSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentBreakdown
        fields = [
            'id', 'section', 'assignment_weightage', 'quiz_weightage',
            'lab_weightage', 'mid_weightage', 'final_weightage', 'project_weightage',
        ]
        read_only_fields = ['id']
