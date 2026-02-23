from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from assessments.models import Question
from assessments.serializers import QuestionSerializer, QuestionWriteSerializer
from api.permissions import IsAdminOrFacultyOrReadOnly

class QuestionListCreateAPI(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrFacultyOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return QuestionWriteSerializer
        return QuestionSerializer

    def get_queryset(self):
        user = self.request.user
        assessment_id = self.kwargs.get('assessment_id')
        qs = Question.objects.filter(assessment_id=assessment_id).prefetch_related('clo')
        
        if user.role == 'student':
            qs = qs.filter(assessment__section__students=user)
        elif user.role == 'faculty':
            qs = qs.filter(assessment__section__faculty=user)
            
        return qs.distinct()


class QuestionDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrFacultyOrReadOnly]

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return QuestionWriteSerializer
        return QuestionSerializer

    def get_queryset(self):
        user = self.request.user
        qs = Question.objects.prefetch_related('clo')
        
        if user.role == 'student':
            qs = qs.filter(assessment__section__students=user)
        elif user.role == 'faculty':
            qs = qs.filter(assessment__section__faculty=user)
            
        return qs.distinct()
