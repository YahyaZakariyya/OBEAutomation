from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from sections.models import Section
from sections.serializers import SectionSerializer, SectionDetailSerializer


class SectionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Section model
    Provides CRUD operations for Sections
    """
    queryset = Section.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SectionDetailSerializer
        return SectionSerializer

    def get_queryset(self):
        queryset = Section.objects.all()
        user = self.request.user

        # Filter by course if provided
        course_id = self.request.query_params.get('course_id', None)
        if course_id:
            queryset = queryset.filter(course__id=course_id)

        # Filter by program if provided
        program_id = self.request.query_params.get('program_id', None)
        if program_id:
            queryset = queryset.filter(program__id=program_id)

        # Filter by faculty if provided
        faculty_id = self.request.query_params.get('faculty_id', None)
        if faculty_id:
            queryset = queryset.filter(faculty__id=faculty_id)

        # Filter by semester if provided
        semester = self.request.query_params.get('semester', None)
        if semester:
            queryset = queryset.filter(semester=semester)

        # Filter by batch if provided
        batch = self.request.query_params.get('batch', None)
        if batch:
            queryset = queryset.filter(batch=batch)

        # Filter by year if provided
        year = self.request.query_params.get('year', None)
        if year:
            queryset = queryset.filter(year=year)

        # Filter by status if provided
        status = self.request.query_params.get('status', None)
        if status:
            queryset = queryset.filter(status=status)

        # Role-based filtering
        if user.role == 'student':
            queryset = queryset.filter(students=user)
        elif user.role == 'faculty':
            view_all = self.request.query_params.get('view_all', 'false')
            if view_all.lower() != 'true':
                queryset = queryset.filter(faculty=user)

        return queryset.order_by('-year', '-batch', 'course__course_id')

    @action(detail=True, methods=['get'])
    def students(self, request, pk=None):
        """Get all students in a section"""
        section = self.get_object()
        from users.serializers import CustomUserSerializer
        students = section.students.all().order_by('username')
        serializer = CustomUserSerializer(students, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_student(self, request, pk=None):
        """Add a student to the section"""
        section = self.get_object()
        student_id = request.data.get('student_id')

        if not student_id:
            return Response(
                {'error': 'student_id is required'},
                status=400
            )

        from users.models import CustomUser
        try:
            student = CustomUser.objects.get(id=student_id, role='student')
            section.students.add(student)
            return Response({'message': 'Student added successfully'})
        except CustomUser.DoesNotExist:
            return Response(
                {'error': 'Student not found'},
                status=404
            )

    @action(detail=True, methods=['post'])
    def remove_student(self, request, pk=None):
        """Remove a student from the section"""
        section = self.get_object()
        student_id = request.data.get('student_id')

        if not student_id:
            return Response(
                {'error': 'student_id is required'},
                status=400
            )

        from users.models import CustomUser
        try:
            student = CustomUser.objects.get(id=student_id, role='student')
            section.students.remove(student)
            return Response({'message': 'Student removed successfully'})
        except CustomUser.DoesNotExist:
            return Response(
                {'error': 'Student not found'},
                status=404
            )

    @action(detail=True, methods=['get'])
    def assessments(self, request, pk=None):
        """Get all assessments for a section"""
        section = self.get_object()
        from assessments.serializers import AssessmentSerializer
        assessments = section.assessments.all().order_by('date')
        serializer = AssessmentSerializer(assessments, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def assessment_breakdown(self, request, pk=None):
        """Get assessment breakdown for a section"""
        section = self.get_object()
        from assessments.serializers import AssessmentBreakdownSerializer
        try:
            breakdown = section.assessmentbreakdown
            serializer = AssessmentBreakdownSerializer(breakdown)
            return Response(serializer.data)
        except:
            return Response(
                {'error': 'Assessment breakdown not found'},
                status=404
            )
