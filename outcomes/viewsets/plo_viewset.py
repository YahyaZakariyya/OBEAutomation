from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from outcomes.models import ProgramLearningOutcome
from outcomes.serializers import PLOSerializer, PLODetailSerializer


class PLOViewSet(viewsets.ModelViewSet):
    """
    ViewSet for ProgramLearningOutcome model
    Provides CRUD operations for PLOs
    """
    queryset = ProgramLearningOutcome.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PLODetailSerializer
        return PLOSerializer

    def get_queryset(self):
        queryset = ProgramLearningOutcome.objects.all()

        # Filter by program if provided
        program_id = self.request.query_params.get('program_id', None)
        if program_id:
            queryset = queryset.filter(program__id=program_id)

        return queryset.order_by('program__program_abbreviation', 'PLO')

    @action(detail=True, methods=['get'])
    def clo_mappings(self, request, pk=None):
        """Get all CLO mappings for this PLO"""
        plo = self.get_object()
        from outcomes.serializers import PloCloMappingSerializer
        mappings = plo.clo_mappings.all()
        serializer = PloCloMappingSerializer(mappings, many=True)
        return Response(serializer.data)
