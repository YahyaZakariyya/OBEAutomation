from rest_framework import serializers
from sections.models import Section


class SectionSerializer(serializers.ModelSerializer):
    course_id = serializers.IntegerField(source='course.id', read_only=True)

    class Meta:
        model = Section
        fields = ['id', 'course_id']


class SectionDetailSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.name', read_only=True)
    course_code = serializers.CharField(source='course.course_id', read_only=True)
    faculty_name = serializers.SerializerMethodField(read_only=True)
    student_count = serializers.SerializerMethodField(read_only=True)
    program_name = serializers.CharField(source='program.program_abbreviation', read_only=True, default=None)

    class Meta:
        model = Section
        fields = [
            'id', 'course', 'program', 'faculty', 'semester', 'section',
            'batch', 'year', 'status', 'course_name', 'course_code',
            'faculty_name', 'student_count', 'program_name',
        ]

    def get_faculty_name(self, obj):
        if obj.faculty:
            return f"{obj.faculty.first_name} {obj.faculty.last_name}"
        return None

    def get_student_count(self, obj):
        return obj.students.count()
