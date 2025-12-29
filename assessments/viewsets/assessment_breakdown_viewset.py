from rest_framework import viewsets, permissions
from assessments.models import AssessmentBreakdown
from assessments.serializers import AssessmentBreakdownSerializer


class AssessmentBreakdownViewSet(viewsets.ModelViewSet):
    """
    ViewSet for AssessmentBreakdown model
    Provides CRUD operations for Assessment Breakdowns
    """
    queryset = AssessmentBreakdown.objects.all()
    serializer_class = AssessmentBreakdownSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = AssessmentBreakdown.objects.all()
        user = self.request.user

        # Filter by section if provided
        section_id = self.request.query_params.get('section_id', None)
        if section_id:
            queryset = queryset.filter(section__id=section_id)

        # Role-based filtering
        if user.role == 'student':
            queryset = queryset.filter(section__students=user)
        elif user.role == 'faculty':
            view_all = self.request.query_params.get('view_all', 'false')
            if view_all.lower() != 'true':
                queryset = queryset.filter(section__faculty=user)

        return queryset
