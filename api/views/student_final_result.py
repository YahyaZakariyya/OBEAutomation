from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from sections.models import Section
from assessments.models import Question, StudentQuestionScore

class StudentFinalResultAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, section_id):
        student = request.user
        
        # Validate the student's enrollment in the section
        section = get_object_or_404(Section, id=section_id, students=student)
        breakdown = section.assessmentbreakdown

        # Retrieve assessments and questions
        assessments = section.assessments.all()
        questions = Question.objects.filter(assessment__in=assessments).prefetch_related('assessment')

        # Group questions by assessment_type
        assessment_types = breakdown.get_assessment_types()
        final_score = 0
        breakdown_data = []

        for assessment_type, weight in assessment_types.items():
            questions_of_type = questions.filter(assessment__type=assessment_type)
            total_marks = sum(q.marks for q in questions_of_type)
            obtained_marks = sum(
                StudentQuestionScore.objects.filter(
                    student=student,
                    question__in=questions_of_type
                ).values_list('marks_obtained', flat=True)
            )
            # Calculate contribution to final score
            percentage = (float(obtained_marks) / float(total_marks)) * 100 if total_marks > 0 else 0
            contribution = (percentage * weight) / 100
            final_score += contribution
            breakdown_data.append({
                "assessment_type": assessment_type,
                "weight": weight,
                "score_contribution": round(contribution, 2)
            })

        return Response({
            "section_id": section_id,
            "final_score": round(final_score, 2),
            "breakdown": breakdown_data
        })
