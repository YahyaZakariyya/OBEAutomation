from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from assessments.models import Assessment
from assessments.serializers import AssessmentSerializer
from api.permissions import IsAdminOrFacultyOrReadOnly

class AssessmentListCreateAPI(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrFacultyOrReadOnly]
    serializer_class = AssessmentSerializer

    def get_queryset(self):
        user = self.request.user
        qs = Assessment.objects.select_related('section__course').prefetch_related('questions')
        
        if user.role == 'student':
            qs = qs.filter(section__students=user)
        elif user.role == 'faculty':
            qs = qs.filter(section__faculty=user)
            
        section_id = self.request.query_params.get('section')
        if section_id:
            qs = qs.filter(section_id=section_id)
        return qs.distinct()

    def perform_create(self, serializer):
        serializer.save()


class AssessmentDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrFacultyOrReadOnly]
    serializer_class = AssessmentSerializer

    def get_queryset(self):
        user = self.request.user
        qs = Assessment.objects.select_related('section__course').prefetch_related('questions')
        
        if user.role == 'student':
            qs = qs.filter(section__students=user)
        elif user.role == 'faculty':
            qs = qs.filter(section__faculty=user)
            
        return qs.distinct()
