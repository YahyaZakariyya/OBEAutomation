from rest_framework import serializers
from outcomes.models import CourseLearningOutcome


class CLOSerializer(serializers.ModelSerializer):
    """Basic CLO serializer"""
    course_id = serializers.PrimaryKeyRelatedField(
        queryset=None,  # Will be set in __init__
        source='course',
        write_only=True
    )
    course_name = serializers.CharField(source='course.name', read_only=True)

    class Meta:
        model = CourseLearningOutcome
        fields = [
            'id',
            'course_id',
            'course_name',
            'CLO',
            'heading',
            'description',
            'weightage',
        ]
        read_only_fields = ['id']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from courses.models import Course
        self.fields['course_id'].queryset = Course.objects.all()


class CLODetailSerializer(serializers.ModelSerializer):
    """Detailed CLO serializer with relationships"""
    course_name = serializers.CharField(source='course.name', read_only=True)
    plo_mappings = serializers.SerializerMethodField()

    class Meta:
        model = CourseLearningOutcome
        fields = [
            'id',
            'course_name',
            'CLO',
            'heading',
            'description',
            'weightage',
            'plo_mappings',
        ]
        read_only_fields = ['id']

    def get_plo_mappings(self, obj):
        mappings = obj.program_mappings.all()
        return [
            {
                'program': mapping.program.program_abbreviation,
                'plo': mapping.plo.PLO,
                'plo_heading': mapping.plo.heading,
                'weightage': mapping.weightage,
            }
            for mapping in mappings
        ]