from rest_framework import viewsets, permissions
from outcomes.models import PloCloMapping
from outcomes.serializers import PloCloMappingSerializer


class PloCloMappingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for PloCloMapping model
    Provides CRUD operations for PLO-CLO Mappings
    """
    queryset = PloCloMapping.objects.all()
    serializer_class = PloCloMappingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = PloCloMapping.objects.all()

        # Filter by program if provided
        program_id = self.request.query_params.get('program_id', None)
        if program_id:
            queryset = queryset.filter(program__id=program_id)

        # Filter by course if provided
        course_id = self.request.query_params.get('course_id', None)
        if course_id:
            queryset = queryset.filter(course__id=course_id)

        # Filter by PLO if provided
        plo_id = self.request.query_params.get('plo_id', None)
        if plo_id:
            queryset = queryset.filter(plo__id=plo_id)

        # Filter by CLO if provided
        clo_id = self.request.query_params.get('clo_id', None)
        if clo_id:
            queryset = queryset.filter(clo__id=clo_id)

        return queryset.order_by('program', 'course', 'plo', 'clo')
