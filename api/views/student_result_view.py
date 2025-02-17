from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from sections.models import Section
from api.services.result_calculation import calculate_student_results

class StudentResultsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        section_id = request.query_params.get('section_id')
        student_id = request.user.id  # Assuming the logged-in user is the student

        if not section_id:
            return Response({"error": "section_id is required"}, status=400)

        try:
            section = Section.objects.get(id=section_id, students__id=student_id)
        except Section.DoesNotExist:
            return Response({"error": "Section not found or not enrolled"}, status=404)

        results = calculate_student_results(section_id, student_id)
        return Response(results)