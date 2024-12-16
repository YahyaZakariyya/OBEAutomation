from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from sections.models import Section
from api.services import compute_clo_attainment

class CLOAttainmentAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, section_id):
        student = request.user
        assessment_type = request.query_params.get('assessment_type')

        try:
            section = Section.objects.get(id=section_id, students=student)
        except Section.DoesNotExist:
            return Response({"error": "Section not found or unauthorized."}, status=404)

        attainment = compute_clo_attainment(student, section, assessment_type)
        return Response({"section": section_id, "attainment": attainment})
