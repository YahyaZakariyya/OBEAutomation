from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Assessment, Question, StudentQuestionScore
from .serializers import QuestionSerializer, StudentSerializer, StudentQuestionScoreSerializer

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
        student_data = StudentSerializer(students, many=True).data

        # Get scores
        scores = StudentQuestionScore.objects.filter(question__assessment=assessment)
        score_data = StudentQuestionScoreSerializer(scores, many=True).data

        return Response({
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
            marks_obtained = score_item['marks_obtained']

            try:
                question = Question.objects.get(id=question_id)

                # Validate marks
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

                # If no errors, update the database
                if not errors:
                    StudentQuestionScore.objects.filter(
                        student_id=student_id,
                        question_id=question_id
                    ).update(marks_obtained=marks_obtained)

            except Question.DoesNotExist:
                errors.append({
                    "student_id": student_id,
                    "question_id": question_id,
                    "error": "Question not found."
                })

        if errors:
            return Response({"status": "error", "errors": errors}, status=400)

        return Response({"status": "success"}, status=200)

def edit_scores_view(request):
    # This view just returns the HTML template
    return render(request, 'obesystem/edit_scores.html')
