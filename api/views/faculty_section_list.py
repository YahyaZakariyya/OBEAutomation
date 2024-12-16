from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from sections.models import Section

class FacultySectionsList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        faculty = request.user
        sections = Section.objects.filter(faculty=faculty)
        data = [{'id': s.id, 'course_name': f"{s.course.code} - {s.course.title}"} for s in sections]
        return Response(data)
