from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from programs.models import Program
from programs.serializers import ProgramSerializer, ProgramListSerializer


class ProgramViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Program model
    Provides CRUD operations for Programs
    """
    queryset = Program.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['program_title', 'program_abbreviation']
    ordering_fields = ['program_abbreviation', 'program_title', 'program_type']
    ordering = ['program_abbreviation']

    def get_serializer_class(self):
        if self.action == 'list':
            return ProgramListSerializer
        return ProgramSerializer

    def get_queryset(self):
        queryset = Program.objects.all()
        user = self.request.user

        # Filter by program type if provided
        program_type = self.request.query_params.get('type', None)
        if program_type:
            queryset = queryset.filter(program_type=program_type)

        # Faculty can see programs they're in charge of
        if user.role == 'faculty':
            view_all = self.request.query_params.get('view_all', 'false')
            if view_all.lower() != 'true':
                queryset = queryset.filter(program_incharge=user)

        return queryset.order_by('program_abbreviation')

    @action(detail=True, methods=['get'])
    def courses(self, request, pk=None):
        """Get all courses for a specific program"""
        program = self.get_object()
        from courses.serializers import CourseSerializer
        courses = program.courses.all()
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def sections(self, request, pk=None):
        """Get all sections for a specific program"""
        program = self.get_object()
        from sections.serializers import SectionSerializer
        sections = program.sections.all()
        serializer = SectionSerializer(sections, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def plos(self, request, pk=None):
        """Get all PLOs for a specific program"""
        program = self.get_object()
        from outcomes.serializers import PLOSerializer
        plos = program.program_outcomes.all()
        serializer = PLOSerializer(plos, many=True)
        return Response(serializer.data)
