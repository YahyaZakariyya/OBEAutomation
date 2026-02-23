from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from programs.models import Program
from programs.serializers import ProgramSerializer
from api.permissions import IsAdminOrReadOnly

class ProgramListCreateAPI(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    queryset = Program.objects.all()
    serializer_class = ProgramSerializer


class ProgramDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    queryset = Program.objects.all()
    serializer_class = ProgramSerializer
