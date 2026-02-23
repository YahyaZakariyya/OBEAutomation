from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from outcomes.models import ProgramLearningOutcome
from outcomes.serializers import PLOSerializer
from api.permissions import IsAdminOrReadOnly

class PLOListCreateAPI(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    serializer_class = PLOSerializer

    def get_queryset(self):
        program_id = self.request.query_params.get('program')
        qs = ProgramLearningOutcome.objects.all()
        if program_id:
            qs = qs.filter(program_id=program_id)
        return qs


class PLODetailAPI(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    queryset = ProgramLearningOutcome.objects.all()
    serializer_class = PLOSerializer
