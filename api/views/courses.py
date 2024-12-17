from rest_framework.response import Response
from rest_framework.views import APIView
from courses.models import Course
from courses.serializers import CourseSerializer
from sections.serializers import SectionSerializer
from sections.models import Section
from rest_framework import status

class CoursesByProgram(APIView):
    def get(self, request, program_id):
        courses = Course.objects.filter(programs=program_id)
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)

class CourseBySection(APIView):
    def get(self, request):
        section_id = request.GET.get('section_id')
        if not section_id:
            return Response({'error': 'Section ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            section = Section.objects.get(pk=section_id)
            serializer = SectionSerializer(section)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Section.DoesNotExist:
            return Response({'error': 'Section not found'}, status=status.HTTP_404_NOT_FOUND)