from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from outcomes.models import CourseLearningOutcome
from outcomes.serializers import CLOSerializer, CLODetailSerializer


class CLOViewSet(viewsets.ModelViewSet):
    """
    ViewSet for CourseLearningOutcome model
    Provides CRUD operations for CLOs
    """
    queryset = CourseLearningOutcome.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CLODetailSerializer
        return CLOSerializer

    def get_queryset(self):
        queryset = CourseLearningOutcome.objects.all()

        # Filter by course if provided
        course_id = self.request.query_params.get('course_id', None)
        if course_id:
            queryset = queryset.filter(course__id=course_id)

        return queryset.order_by('course__course_id', 'CLO')

    @action(detail=True, methods=['get'])
    def plo_mappings(self, request, pk=None):
        """Get all PLO mappings for this CLO"""
        clo = self.get_object()
        from outcomes.serializers import PloCloMappingSerializer
        mappings = clo.program_mappings.all()
        serializer = PloCloMappingSerializer(mappings, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def questions(self, request, pk=None):
        """Get all questions mapped to this CLO"""
        clo = self.get_object()
        from assessments.serializers import QuestionSerializer
        questions = clo.questions.all()
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data)
