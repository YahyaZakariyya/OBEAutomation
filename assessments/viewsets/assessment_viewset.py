from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from assessments.models import Assessment
from assessments.serializers import AssessmentSerializer, AssessmentDetailSerializer


class AssessmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Assessment model
    Provides CRUD operations for Assessments
    """
    queryset = Assessment.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return AssessmentDetailSerializer
        return AssessmentSerializer

    def get_queryset(self):
        queryset = Assessment.objects.all()
        user = self.request.user

        # Filter by section if provided
        section_id = self.request.query_params.get('section_id', None)
        if section_id:
            queryset = queryset.filter(section__id=section_id)

        # Filter by type if provided
        assessment_type = self.request.query_params.get('type', None)
        if assessment_type:
            queryset = queryset.filter(type=assessment_type)

        # Role-based filtering
        if user.role == 'student':
            queryset = queryset.filter(section__students=user)
        elif user.role == 'faculty':
            view_all = self.request.query_params.get('view_all', 'false')
            if view_all.lower() != 'true':
                queryset = queryset.filter(section__faculty=user)

        return queryset.order_by('-date')

    @action(detail=True, methods=['get'])
    def questions(self, request, pk=None):
        """Get all questions for an assessment"""
        assessment = self.get_object()
        from assessments.serializers import QuestionSerializer
        questions = assessment.questions.all()
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Get statistics for an assessment"""
        assessment = self.get_object()
        questions = assessment.questions.all()
        total_marks = assessment.get_total_marks()

        # Calculate student statistics
        from assessments.models import StudentQuestionScore
        section_students = assessment.section.students.all()
        student_scores = []

        for student in section_students:
            student_total = 0
            for question in questions:
                try:
                    score = StudentQuestionScore.objects.get(
                        student=student,
                        question=question
                    )
                    student_total += score.marks_obtained
                except StudentQuestionScore.DoesNotExist:
                    pass

            if total_marks > 0:
                percentage = (student_total / total_marks) * 100
            else:
                percentage = 0

            student_scores.append({
                'student_id': student.id,
                'student_name': student.get_full_name(),
                'score': student_total,
                'percentage': percentage
            })

        # Calculate average
        if student_scores:
            avg_score = sum(s['score'] for s in student_scores) / len(student_scores)
            avg_percentage = sum(s['percentage'] for s in student_scores) / len(student_scores)
        else:
            avg_score = 0
            avg_percentage = 0

        return Response({
            'total_marks': total_marks,
            'questions_count': questions.count(),
            'students_count': section_students.count(),
            'average_score': avg_score,
            'average_percentage': avg_percentage,
            'student_scores': student_scores
        })
