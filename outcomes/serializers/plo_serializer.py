from rest_framework import serializers
from outcomes.models import ProgramLearningOutcome


class PLOSerializer(serializers.ModelSerializer):
    """Basic PLO serializer"""
    program_id = serializers.PrimaryKeyRelatedField(
        queryset=None,  # Will be set in __init__
        source='program',
        write_only=True
    )
    program_name = serializers.CharField(source='program.program_abbreviation', read_only=True)

    class Meta:
        model = ProgramLearningOutcome
        fields = [
            'id',
            'program_id',
            'program_name',
            'PLO',
            'heading',
            'description',
            'weightage',
        ]
        read_only_fields = ['id']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from programs.models import Program
        self.fields['program_id'].queryset = Program.objects.all()


class PLODetailSerializer(serializers.ModelSerializer):
    """Detailed PLO serializer with CLO mappings"""
    program_name = serializers.CharField(source='program.program_abbreviation', read_only=True)
    clo_mappings = serializers.SerializerMethodField()

    class Meta:
        model = ProgramLearningOutcome
        fields = [
            'id',
            'program_name',
            'PLO',
            'heading',
            'description',
            'weightage',
            'clo_mappings',
        ]
        read_only_fields = ['id']

    def get_clo_mappings(self, obj):
        mappings = obj.clo_mappings.all()
        return [
            {
                'course': mapping.course.name,
                'clo': mapping.clo.CLO,
                'clo_heading': mapping.clo.heading,
                'weightage': mapping.weightage,
            }
            for mapping in mappings
        ]