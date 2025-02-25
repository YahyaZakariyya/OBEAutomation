from rest_framework.views import APIView
from rest_framework.response import Response
from assessments.models import Assessment, Question, StudentQuestionScore
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from assessments.serializers import QuestionSerializer, StudentQuestionScoreSerializer
from users.serializers import CustomUserSerializer

class MarksAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        assessment_id = request.query_params.get('id')
        assessment = get_object_or_404(Assessment, id=assessment_id)

        # Get questions
        questions = Question.objects.filter(assessment=assessment)
        question_data = QuestionSerializer(questions, many=True).data

        # Get students
        students = assessment.section.students.all()
        student_data = CustomUserSerializer(students, many=True).data

        # Get scores
        scores = StudentQuestionScore.objects.filter(question__assessment=assessment)
        score_data = StudentQuestionScoreSerializer(scores, many=True).data

        return Response({
            'assessment_title': assessment.title,
            'questions': question_data,
            'students': student_data,
            'scores': score_data
        })

    def post(self, request):
        # Expecting data in the form: { "scores": [{ "student_id": x, "question_id": y, "marks_obtained": z }, ...] }
        data = request.data.get('scores', [])
        errors = []

        for score_item in data:
            student_id = score_item['student_id']
            question_id = score_item['question_id']
            
            # ✅ Convert marks_obtained to float to handle decimal values
            try:
                marks_obtained = float(score_item['marks_obtained']) if score_item['marks_obtained'] else 0.0
            except ValueError:
                return Response({
                    "status": "error",
                    "message": f"Invalid marks format for student {student_id}, question {question_id}"
                }, status=400)

            try:
                question = Question.objects.get(id=question_id)

                # ✅ Validate Marks (No Negative & Not More Than Max Marks)
                if marks_obtained < 0:
                    errors.append({
                        "student_id": student_id,
                        "question_id": question_id,
                        "error": "Marks cannot be negative."
                    })
                elif marks_obtained > question.marks:
                    errors.append({
                        "student_id": student_id,
                        "question_id": question_id,
                        "error": f"Marks cannot exceed {question.marks}."
                    })

                if not errors:
                    StudentQuestionScore.objects.update_or_create(
                        student_id=student_id,
                        question_id=question_id,
                        defaults={"marks_obtained": marks_obtained}
                    )

            except Question.DoesNotExist:
                errors.append({
                    "student_id": student_id,
                    "question_id": question_id,
                    "error": "Question not found."
                })