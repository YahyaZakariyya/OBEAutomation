from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from outcomes.models import CourseLearningOutcome
from outcomes.serializers import CLOSerializer
from api.permissions import IsAdminOrReadOnly

class CLOListCreateAPI(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    serializer_class = CLOSerializer

    def get_queryset(self):
        course_id = self.request.query_params.get('course')
        qs = CourseLearningOutcome.objects.all()
        if course_id:
            qs = qs.filter(course_id=course_id)
        return qs


class CLODetailAPI(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    queryset = CourseLearningOutcome.objects.all()
    serializer_class = CLOSerializer
