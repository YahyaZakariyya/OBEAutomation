from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from sections.models import Section
from guardian.shortcuts import get_objects_for_user

class SectionsAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        sections = get_objects_for_user(user, 'view_section', Section)

        data = [{'id': section.id, 'name': f"{section.course.name} - {section.semester}{section.section}"} for section in sections]
        return Response(data)
