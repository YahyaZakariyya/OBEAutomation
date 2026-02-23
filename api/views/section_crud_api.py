from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from sections.models import Section
from sections.serializers import SectionDetailSerializer
from users.serializers import CustomUserSerializer
from users.models import CustomUser
from api.permissions import IsAdminOrReadOnly

class SectionListCreateAPI(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    serializer_class = SectionDetailSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Section.objects.select_related('course', 'program', 'faculty').all()
        elif user.role == 'faculty':
            return Section.objects.select_related('course', 'program', 'faculty').filter(faculty=user)
        else:
            return Section.objects.select_related('course', 'program', 'faculty').filter(students=user)


class SectionDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    serializer_class = SectionDetailSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Section.objects.select_related('course', 'program', 'faculty').all()
        elif user.role == 'faculty':
            return Section.objects.select_related('course', 'program', 'faculty').filter(faculty=user)
        else:
            return Section.objects.select_related('course', 'program', 'faculty').filter(students=user)


class SectionStudentsAPI(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    def get(self, request, pk):
        section = Section.objects.get(pk=pk)
        students = section.students.all()
        serializer = CustomUserSerializer(students, many=True)
        return Response(serializer.data)

    def post(self, request, pk):
        section = Section.objects.get(pk=pk)
        student_ids = request.data.get('student_ids', [])
        students = CustomUser.objects.filter(id__in=student_ids, role='student')
        section.students.add(*students)
        return Response({'status': 'students added'}, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        section = Section.objects.get(pk=pk)
        student_ids = request.data.get('student_ids', [])
        students = CustomUser.objects.filter(id__in=student_ids)
        section.students.remove(*students)
        return Response({'status': 'students removed'}, status=status.HTTP_200_OK)
