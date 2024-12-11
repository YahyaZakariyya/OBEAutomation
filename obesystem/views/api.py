from rest_framework.views import APIView
from rest_framework.response import Response
from obesystem.utils.calculations import calculate_clo_attainment, calculate_plo_attainment
from obesystem.models import CourseLearningOutcome, ProgramLearningOutcome, Assessment, Question, StudentQuestionScore, Section
from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from obesystem.serializers import QuestionSerializer, StudentSerializer, StudentQuestionScoreSerializer
from rest_framework import status
from guardian.shortcuts import get_objects_for_user
from decimal import Decimal

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


class CLOPerformanceAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        student = request.user  # Logged-in user
        section_id = request.GET.get('section_id')

        # Fetch sections the student is allowed to access
        allowed_sections = get_objects_for_user(student, 'view_section', Section)

        # Validate the provided section_id
        if not section_id:
            return Response({"error": "Missing section_id"}, status=status.HTTP_400_BAD_REQUEST)
        if not allowed_sections.filter(id=section_id).exists():
            return Response({"error": "Access denied for this section"}, status=status.HTTP_403_FORBIDDEN)

        # Fetch CLOs and calculate performance
        clos = CourseLearningOutcome.objects.filter(course__sections__id=section_id)
        data = []

        for clo in clos:
            questions = Question.objects.filter(clo=clo)
            total_marks = sum(question.marks for question in questions) if questions.exists() else 0
            obtained_marks = sum(
                score.marks_obtained or 0
                for question in questions
                for score in question.studentquestionscore_set.filter(student_id=student.id)
            ) if questions.exists() else 0

            attainment = (
                (Decimal(obtained_marks) / Decimal(total_marks)) * 100
                if total_marks > 0 else Decimal(100)
            )

            data.append({
                "name": clo.heading,
                "description": clo.description,
                "attainment": attainment,
                "code": clo.CLO,
                "total_marks": total_marks,
                "obtained_marks": obtained_marks,
                "assessments": list(questions.values_list('assessment__title', flat=True)) if questions.exists() else [],
            })

        return Response(data)
    
from django.db.models import Avg, Max, Min

class FacultyCLOAnalysisAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        faculty_sections = get_objects_for_user(request.user, 'view_section', Section)
        section_id = request.GET.get('section_id')
        program_id = request.GET.get('program')
        assessment_type = request.GET.get('assessmentType')

        if section_id and not faculty_sections.filter(id=section_id).exists():
            return Response({"error": "Access denied for this section"}, status=403)

        query = faculty_sections
        if section_id:
            query = query.filter(id=section_id)
        if program_id:
            query = query.filter(program_id=program_id)

        results = []
        for section in query:
            clos = CourseLearningOutcome.objects.filter(course__sections=section)
            section_name = section.name if hasattr(section, "name") else "Unnamed Section"

            section_data = {
                "section": section_name,
                "average_clo_attainment": 0,
                "highest_performing_student": "N/A",
                "lowest_performing_student": "N/A",
                "clos": []
            }

            total_clo_attainment = 0
            for clo in clos:
                questions = Question.objects.filter(clo=clo)
                total_marks = sum(Decimal(question.marks) for question in questions) if questions.exists() else 0
                obtained_marks = sum(
                    Decimal(score.marks_obtained or 0)
                    for question in questions
                    for score in question.studentquestionscore_set.all()
                ) if questions.exists() else 0

                attainment = (
                    (Decimal(obtained_marks) / Decimal(total_marks)) * 100
                    if total_marks > 0 else Decimal(100)
                )

                section_data["clos"].append({
                    "name": clo.heading,
                    "description": clo.description,
                    "attainment": float(attainment),
                    "total_marks": float(total_marks),
                    "obtained_marks": float(obtained_marks),
                })

                total_clo_attainment += attainment

            section_data["average_clo_attainment"] = float(
                total_clo_attainment / len(clos) if clos.exists() else 0
            )

            highest_student = StudentQuestionScore.objects.filter(
                question__clo__course__sections=section
            ).aggregate(Max('marks_obtained'))['marks_obtained__max'] or "N/A"
            lowest_student = StudentQuestionScore.objects.filter(
                question__clo__course__sections=section
            ).aggregate(Min('marks_obtained'))['marks_obtained__min'] or "N/A"

            section_data["highest_performing_student"] = highest_student
            section_data["lowest_performing_student"] = lowest_student

            results.append(section_data)

        return Response(results)
    
    
class PLOPerformanceAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        student_id = request.GET.get('student_id')
        section_id = request.GET.get('section_id')
        plos = ProgramLearningOutcome.objects.filter(program__sections__id=section_id)

        data = [
            {"name": plo.heading, "attainment": calculate_plo_attainment(plo, student_id)}
            for plo in plos
        ]
        return Response(data)


