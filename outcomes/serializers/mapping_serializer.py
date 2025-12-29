from rest_framework import serializers
from outcomes.models import PloCloMapping


class PloCloMappingSerializer(serializers.ModelSerializer):
    """PLO-CLO Mapping serializer"""
    program_id = serializers.PrimaryKeyRelatedField(
        queryset=None,  # Will be set in __init__
        source='program',
        write_only=True
    )
    course_id = serializers.PrimaryKeyRelatedField(
        queryset=None,  # Will be set in __init__
        source='course',
        write_only=True
    )
    plo_id = serializers.PrimaryKeyRelatedField(
        queryset=None,  # Will be set in __init__
        source='plo',
        write_only=True
    )
    clo_id = serializers.PrimaryKeyRelatedField(
        queryset=None,  # Will be set in __init__
        source='clo',
        write_only=True
    )

    program_name = serializers.CharField(source='program.program_abbreviation', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)
    plo_number = serializers.IntegerField(source='plo.PLO', read_only=True)
    clo_number = serializers.IntegerField(source='clo.CLO', read_only=True)

    class Meta:
        model = PloCloMapping
        fields = [
            'id',
            'program_id',
            'program_name',
            'course_id',
            'course_name',
            'plo_id',
            'plo_number',
            'clo_id',
            'clo_number',
            'weightage',
        ]
        read_only_fields = ['id']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from programs.models import Program
        from courses.models import Course
        from outcomes.models import ProgramLearningOutcome, CourseLearningOutcome
        self.fields['program_id'].queryset = Program.objects.all()
        self.fields['course_id'].queryset = Course.objects.all()
        self.fields['plo_id'].queryset = ProgramLearningOutcome.objects.all()
        self.fields['clo_id'].queryset = CourseLearningOutcome.objects.all()
