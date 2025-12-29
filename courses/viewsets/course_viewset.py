from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from courses.models import Course
from courses.serializers import CourseSerializer, CourseDetailSerializer


class CourseViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Course model
    Provides CRUD operations for Courses
    """
    queryset = Course.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['course_id', 'name']
    ordering_fields = ['course_id', 'name', 'credit_hours']
    ordering = ['course_id']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CourseDetailSerializer
        return CourseSerializer

    def get_queryset(self):
        queryset = Course.objects.all()

        # Filter by program if provided
        program_id = self.request.query_params.get('program_id', None)
        if program_id:
            queryset = queryset.filter(programs__id=program_id)

        # Filter by credit hours if provided
        credit_hours = self.request.query_params.get('credit_hours', None)
        if credit_hours:
            queryset = queryset.filter(credit_hours=credit_hours)

        # Search by name or course_id
        search = self.request.query_params.get('search', None)
        if search:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(course_id__icontains=search)
            )

        return queryset.order_by('course_id')

    @action(detail=True, methods=['get'])
    def clos(self, request, pk=None):
        """Get all CLOs for a specific course"""
        course = self.get_object()
        from outcomes.serializers import CLOSerializer
        clos = course.course_outcomes.all().order_by('CLO')
        serializer = CLOSerializer(clos, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def sections(self, request, pk=None):
        """Get all sections for a specific course"""
        course = self.get_object()
        from sections.serializers import SectionSerializer
        sections = course.sections.all()
        serializer = SectionSerializer(sections, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def programs(self, request, pk=None):
        """Get all programs offering this course"""
        course = self.get_object()
        from programs.serializers import ProgramListSerializer
        programs = course.programs.all()
        serializer = ProgramListSerializer(programs, many=True)
        return Response(serializer.data)
