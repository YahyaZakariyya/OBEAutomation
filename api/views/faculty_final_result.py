from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from sections.models import Section
from assessments.models import Question, StudentQuestionScore


class FacultyFinalResultsAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, section_id):
        faculty = request.user

        # Validate faculty is assigned to the section
        section = get_object_or_404(Section, id=section_id, faculty=faculty)
        breakdown = section.assessmentbreakdown.get_assessment_types()
        students = section.students.all()
        assessments = section.assessments.all()

        # Group assessments by type
        assessment_groups = {}
        for assessment in assessments:
            assessment_groups.setdefault(assessment.type, []).append(assessment)

        results = []
        combined_breakdown = []
        solo_breakdown = []

        # Iterate through all students
        for student in students:
            total_score = 0
            student_solo_breakdown = []
            student_combined_breakdown = []

            # Iterate through each assessment type
            for assessment_type, type_weight in breakdown.items():
                type_total_marks = 0
                type_obtained_marks = 0

                # Process individual assessments within this type
                for assessment in assessment_groups.get(assessment_type, []):
                    questions = Question.objects.filter(assessment=assessment)
                    assessment_total_marks = sum(q.marks for q in questions)
                    assessment_obtained_marks = sum(
                        StudentQuestionScore.objects.filter(
                            student=student, question__in=questions
                        ).values_list('marks_obtained', flat=True)
                    )

                    # Scale individual assessment contribution
                    if assessment_total_marks > 0:
                        assessment_percentage = (float(assessment_obtained_marks) / float(assessment_total_marks)) * type_weight
                    else:
                        assessment_percentage = 0

                    student_solo_breakdown.append({
                        "assessment_id": assessment.id,
                        "assessment_name": assessment.title,
                        "assessment_type": assessment.type,
                        "weightage_within_type": assessment.weightage,
                        "score_contribution": round(assessment_percentage, 2),
                    })

                    # Aggregate type totals
                    type_total_marks += assessment_total_marks
                    type_obtained_marks += assessment_obtained_marks

                # Calculate combined type contribution
                if type_total_marks > 0:
                    type_percentage = (float(type_obtained_marks) / float(type_total_marks)) * type_weight
                else:
                    type_percentage = 0

                student_combined_breakdown.append({
                    "assessment_type": assessment_type,
                    "weightage": type_weight,
                    "score_contribution": round(type_percentage, 2),
                })

                # Add to total score
                total_score += type_percentage

            results.append({
                "student_id": student.id,
                "student_name": student.get_full_name(),
                "final_score": round(total_score, 2),
                "combined_breakdown": student_combined_breakdown,
                "solo_breakdown": student_solo_breakdown,
            })

        # Calculate average score for the section
        average_score = round(sum(r['final_score'] for r in results) / len(results), 2) if results else 0

        return Response({
            "section_id": section_id,
            "average_score": average_score,
            "students": results,
        })
