from rest_framework import serializers
from sections.models import Section
from courses.serializers import CourseSerializer
from programs.serializers import ProgramListSerializer
from users.serializers import CustomUserSerializer


class SectionSerializer(serializers.ModelSerializer):
    """Basic Section serializer"""
    course = CourseSerializer(read_only=True)
    course_id = serializers.PrimaryKeyRelatedField(
        queryset=None,  # Will be set in __init__
        source='course',
        write_only=True
    )
    program = ProgramListSerializer(read_only=True)
    program_id = serializers.PrimaryKeyRelatedField(
        queryset=None,  # Will be set in __init__
        source='program',
        write_only=True,
        required=False,
        allow_null=True
    )
    faculty = CustomUserSerializer(read_only=True)
    faculty_id = serializers.PrimaryKeyRelatedField(
        queryset=None,  # Will be set in __init__
        source='faculty',
        write_only=True,
        required=False,
        allow_null=True
    )
    section_display = serializers.SerializerMethodField()

    class Meta:
        model = Section
        fields = [
            'id',
            'course',
            'course_id',
            'program',
            'program_id',
            'faculty',
            'faculty_id',
            'semester',
            'section',
            'batch',
            'year',
            'status',
            'section_display',
        ]
        read_only_fields = ['id']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Import here to avoid circular imports
        from courses.models import Course
        from programs.models import Program
        from users.models import CustomUser
        self.fields['course_id'].queryset = Course.objects.all()
        self.fields['program_id'].queryset = Program.objects.all()
        self.fields['faculty_id'].queryset = CustomUser.objects.filter(role='faculty')

    def get_section_display(self, obj):
        return str(obj)


class SectionDetailSerializer(serializers.ModelSerializer):
    """Detailed Section serializer with all relationships"""
    course = CourseSerializer(read_only=True)
    program = ProgramListSerializer(read_only=True)
    faculty = CustomUserSerializer(read_only=True)
    students = CustomUserSerializer(many=True, read_only=True)
    students_count = serializers.SerializerMethodField()
    assessments_count = serializers.SerializerMethodField()
    section_display = serializers.SerializerMethodField()

    class Meta:
        model = Section
        fields = [
            'id',
            'course',
            'program',
            'faculty',
            'semester',
            'section',
            'batch',
            'year',
            'status',
            'students',
            'students_count',
            'assessments_count',
            'section_display',
        ]
        read_only_fields = ['id']

    def get_students_count(self, obj):
        return obj.students.count()

    def get_assessments_count(self, obj):
        return obj.assessments.count()

    def get_section_display(self, obj):
        return str(obj)
