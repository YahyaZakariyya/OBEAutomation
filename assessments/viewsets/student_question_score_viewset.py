from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from assessments.models import StudentQuestionScore
from assessments.serializers import (
    StudentQuestionScoreSerializer,
    StudentQuestionScoreDetailSerializer
)


class StudentQuestionScoreViewSet(viewsets.ModelViewSet):
    """
    ViewSet for StudentQuestionScore model
    Provides CRUD operations for Student Question Scores
    """
    queryset = StudentQuestionScore.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return StudentQuestionScoreDetailSerializer
        return StudentQuestionScoreSerializer

    def get_queryset(self):
        queryset = StudentQuestionScore.objects.all()
        user = self.request.user

        # Filter by student if provided
        student_id = self.request.query_params.get('student_id', None)
        if student_id:
            queryset = queryset.filter(student__id=student_id)

        # Filter by question if provided
        question_id = self.request.query_params.get('question_id', None)
        if question_id:
            queryset = queryset.filter(question__id=question_id)

        # Filter by assessment if provided
        assessment_id = self.request.query_params.get('assessment_id', None)
        if assessment_id:
            queryset = queryset.filter(question__assessment__id=assessment_id)

        # Filter by section if provided
        section_id = self.request.query_params.get('section_id', None)
        if section_id:
            queryset = queryset.filter(question__assessment__section__id=section_id)

        # Role-based filtering
        if user.role == 'student':
            queryset = queryset.filter(student=user)
        elif user.role == 'faculty':
            view_all = self.request.query_params.get('view_all', 'false')
            if view_all.lower() != 'true':
                queryset = queryset.filter(question__assessment__section__faculty=user)

        return queryset

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """Bulk create or update student question scores"""
        scores_data = request.data.get('scores', [])

        if not scores_data:
            return Response(
                {'error': 'scores data is required'},
                status=400
            )

        created = []
        updated = []
        errors = []

        for score_data in scores_data:
            try:
                student_id = score_data.get('student_id')
                question_id = score_data.get('question_id')
                marks_obtained = score_data.get('marks_obtained')

                if not all([student_id, question_id, marks_obtained is not None]):
                    errors.append({
                        'data': score_data,
                        'error': 'Missing required fields'
                    })
                    continue

                from users.models import CustomUser
                from assessments.models import Question

                student = CustomUser.objects.get(id=student_id)
                question = Question.objects.get(id=question_id)

                score, is_created = StudentQuestionScore.objects.update_or_create(
                    student=student,
                    question=question,
                    defaults={'marks_obtained': marks_obtained}
                )

                if is_created:
                    created.append(StudentQuestionScoreSerializer(score).data)
                else:
                    updated.append(StudentQuestionScoreSerializer(score).data)

            except Exception as e:
                errors.append({
                    'data': score_data,
                    'error': str(e)
                })

        return Response({
            'created': created,
            'updated': updated,
            'errors': errors
        })
