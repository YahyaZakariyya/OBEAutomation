from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from courses.models import Course
from courses.serializers import CourseSerializer
from api.permissions import IsAdminOrReadOnly

class CourseListCreateAPI(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    queryset = Course.objects.all()
    serializer_class = CourseSerializer


class CourseDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
