from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from assessments.models import Question
from assessments.serializers import QuestionSerializer, QuestionDetailSerializer


class QuestionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Question model
    Provides CRUD operations for Questions
    """
    queryset = Question.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return QuestionDetailSerializer
        return QuestionSerializer

    def get_queryset(self):
        queryset = Question.objects.all()
        user = self.request.user

        # Filter by assessment if provided
        assessment_id = self.request.query_params.get('assessment_id', None)
        if assessment_id:
            queryset = queryset.filter(assessment__id=assessment_id)

        # Filter by CLO if provided
        clo_id = self.request.query_params.get('clo_id', None)
        if clo_id:
            queryset = queryset.filter(clo__id=clo_id)

        # Role-based filtering
        if user.role == 'student':
            queryset = queryset.filter(assessment__section__students=user)
        elif user.role == 'faculty':
            view_all = self.request.query_params.get('view_all', 'false')
            if view_all.lower() != 'true':
                queryset = queryset.filter(assessment__section__faculty=user)

        return queryset

    @action(detail=True, methods=['get'])
    def scores(self, request, pk=None):
        """Get all student scores for this question"""
        question = self.get_object()
        from assessments.serializers import StudentQuestionScoreSerializer
        scores = question.student_scores.all()
        serializer = StudentQuestionScoreSerializer(scores, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Get statistics for this question"""
        question = self.get_object()
        scores = question.student_scores.all()

        if scores.exists():
            total_students = scores.count()
            total_marks = question.marks
            avg_marks = sum(s.marks_obtained for s in scores) / total_students
            avg_percentage = (avg_marks / total_marks) * 100 if total_marks > 0 else 0
            max_marks = max(s.marks_obtained for s in scores)
            min_marks = min(s.marks_obtained for s in scores)
        else:
            total_students = 0
            avg_marks = 0
            avg_percentage = 0
            max_marks = 0
            min_marks = 0

        return Response({
            'total_marks': question.marks,
            'total_students': total_students,
            'average_marks': avg_marks,
            'average_percentage': avg_percentage,
            'max_marks': max_marks,
            'min_marks': min_marks
        })
