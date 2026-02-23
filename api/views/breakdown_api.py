from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from assessments.models import AssessmentBreakdown
from assessments.serializers import AssessmentBreakdownSerializer


class BreakdownAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, section_id):
        try:
            breakdown = AssessmentBreakdown.objects.get(section_id=section_id)
            serializer = AssessmentBreakdownSerializer(breakdown)
            return Response(serializer.data)
        except AssessmentBreakdown.DoesNotExist:
            return Response({'detail': 'No breakdown found for this section.'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, section_id):
        try:
            breakdown = AssessmentBreakdown.objects.get(section_id=section_id)
        except AssessmentBreakdown.DoesNotExist:
            data = {**request.data, 'section': section_id}
            serializer = AssessmentBreakdownSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer = AssessmentBreakdownSerializer(breakdown, data={**request.data, 'section': section_id})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
