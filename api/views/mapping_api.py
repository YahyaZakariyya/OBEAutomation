from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from outcomes.models import PloCloMapping
from outcomes.serializers import PloCloMappingSerializer
from api.permissions import IsAdminOrReadOnly

class MappingListCreateAPI(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    serializer_class = PloCloMappingSerializer

    def get_queryset(self):
        qs = PloCloMapping.objects.select_related('plo', 'clo').all()
        program_id = self.request.query_params.get('program')
        course_id = self.request.query_params.get('course')
        if program_id:
            qs = qs.filter(program_id=program_id)
        if course_id:
            qs = qs.filter(course_id=course_id)
        return qs


class MappingDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    queryset = PloCloMapping.objects.select_related('plo', 'clo').all()
    serializer_class = PloCloMappingSerializer
