from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from sections.models import Section
from api.services import compute_clo_attainment_for_faculty

class FacultyCLOAttainment(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, section_id):
        faculty = request.user
        assessment_type = request.GET.get('assessment_type', None)

        # Validate faculty is assigned to the section
        try:
            section = Section.objects.get(id=section_id, faculty=faculty)
        except Section.DoesNotExist:
            return Response({"error": "Invalid section or unauthorized access."}, status=400)

        result = compute_clo_attainment_for_faculty(faculty, section, assessment_type)
        return Response(result)
