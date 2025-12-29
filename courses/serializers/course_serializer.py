from rest_framework import serializers
from courses.models import Course


class CourseSerializer(serializers.ModelSerializer):
    """Basic Course serializer"""
    class Meta:
        model = Course
        fields = ['id', 'course_id', 'name', 'credit_hours']
        read_only_fields = ['id']


class CourseDetailSerializer(serializers.ModelSerializer):
    """Detailed Course serializer with relationships"""
    programs = serializers.SerializerMethodField()
    clos_count = serializers.SerializerMethodField()
    sections_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id',
            'course_id',
            'name',
            'credit_hours',
            'programs',
            'clos_count',
            'sections_count',
        ]
        read_only_fields = ['id']

    def get_programs(self, obj):
        from programs.serializers import ProgramListSerializer
        return ProgramListSerializer(obj.programs.all(), many=True).data

    def get_clos_count(self, obj):
        return obj.course_outcomes.count()

    def get_sections_count(self, obj):
        return obj.sections.count()