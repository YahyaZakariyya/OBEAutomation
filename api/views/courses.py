from rest_framework.response import Response
from rest_framework.views import APIView
from courses.models import Course
from courses.serializers import CourseSerializer

class CoursesByProgram(APIView):    
    def get(self, request, program_id):
        courses = Course.objects.filter(programs=program_id)
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)