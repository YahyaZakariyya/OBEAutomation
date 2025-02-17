from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from users.models import CustomUser
from assessments.models import Question, StudentQuestionScore
from users.serializers import CustomUserSerializer

class StudentScoreAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        student_id = request.query_params.get('student_id')
        assessment_id = request.query_params.get('assessment_id')

        # ✅ Ensure the requesting user is a student & is viewing their own scores
        if request.user.role != 'student' or str(request.user.id) != student_id:
            print('this is failed')
            return Response({"error": "Unauthorized access."}, status=403)

        # ✅ Fetch student details
        student = get_object_or_404(CustomUser, id=student_id)
        student_data = CustomUserSerializer(student).data

        # ✅ Fetch all questions for the given assessment
        questions = Question.objects.filter(assessment_id=assessment_id)
        if not questions.exists():
            return Response({"error": "No questions found for this assessment."}, status=404)

        # ✅ Fetch CLOs, Total Marks, and Student Marks
        question_numbers = []
        clos_mapping = []
        total_marks = []
        obtained_marks = []

        for index, question in enumerate(questions, start=1):
            question_numbers.append(f"Q{index}")  # ✅ Dynamic question numbering
            total_marks.append(question.marks)

            # Fetch CLOs mapped to the question
            clos = question.clo.all().values_list('CLO', flat=True)  # ✅ Fetch CLO names
            clos_mapping.append(list(clos))

            # Fetch student's obtained marks for this question
            student_score = StudentQuestionScore.objects.filter(student=student, question=question).first()
            obtained_marks.append(student_score.marks_obtained if student_score else 0)

        # ✅ Construct Response Data
        response_data = {
            "student": student_data,
            "table": {
                "questions": question_numbers,
                "clos": clos_mapping,
                "total_marks": total_marks,
                "obtained_marks": obtained_marks
            }
        }

        return Response(response_data, status=200)
