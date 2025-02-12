from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum
from assessments.models import Assessment, Question, StudentQuestionScore
from sections.models import Section
from outcomes.models import CourseLearningOutcome
from assessments.models import AssessmentBreakdown


class FacultyCLOAttainmentAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, section_id):
        """
        API to fetch summarized OBE result details for a given section.
        """

        # Get Section
        section = Section.objects.filter(id=section_id).first()
        if not section:
            return Response({"status": "error", "message": "Section not found"}, status=404)

        course = section.course
        faculty = section.faculty

        # Get the Assessment Breakdown
        breakdown = AssessmentBreakdown.objects.filter(section=section).first()
        if not breakdown:
            return Response({"status": "error", "message": "Assessment Breakdown not found"}, status=404)

        assessment_weights = breakdown.get_assessment_types()

        # Get all CLOs for the Course
        clos = CourseLearningOutcome.objects.filter(course=course)

        # CLO Data Structure
        clo_lookup = {
            clo.id: {
                "cloCode": f"CLO{clo.CLO}",
                "title": clo.heading,
                "weightage": clo.weightage,
                "totalMarks": 0,
                "assessmentTypeContribution": {},  # Contribution of each assessment type
            }
            for clo in clos
        }

        # Get All Assessments for the Section
        assessments = Assessment.objects.filter(section=section)
        assessment_data = []

        for assessment in assessments:
            assessment_category_weightage = assessment_weights.get(assessment.type, 0)
            effectiveAssessmentWeightage = (assessment.weightage / 100) * assessment_category_weightage

            assessment_info = {
                "assessmentId": assessment.id,
                "assessmentTitle": assessment.title,
                "assessmentType": assessment.type,
                "effectiveAssessmentWeightage": round(effectiveAssessmentWeightage, 2)
            }

            # Get all Questions under this Assessment
            questions = Question.objects.filter(assessment=assessment)
            total_question_marks = sum(q.marks for q in questions)

            for question in questions:
                normalized_question_weight = (question.marks / total_question_marks) * effectiveAssessmentWeightage

                # Get CLOs mapped to this question
                mapped_clos = question.clo.all()
                num_clos = mapped_clos.count()

                for clo in mapped_clos:
                    distribution_factor = 1 / num_clos
                    if assessment.type not in clo_lookup[clo.id]["assessmentTypeContribution"]:
                        clo_lookup[clo.id]["assessmentTypeContribution"][assessment.type] = 0

                    clo_lookup[clo.id]["assessmentTypeContribution"][assessment.type] += round(
                        normalized_question_weight * distribution_factor, 2
                    )

            assessment_data.append(assessment_info)

        # Final CLO Calculation with Assessment Contribution
        final_clo_data = []
        for clo_id, clo_info in clo_lookup.items():
            total_clo_marks = sum(clo_info["assessmentTypeContribution"].values())

            clo_info["assessmentTypeContributionPercentage"] = {
                key: round((value / total_clo_marks) * 100, 2) if total_clo_marks > 0 else 0
                for key, value in clo_info["assessmentTypeContribution"].items()
            }

            clo_info["totalMarks"] = round(total_clo_marks, 2)
            del clo_info["assessmentTypeContribution"]
            final_clo_data.append(clo_info)

        response_data = {
            "status": "success",
            "message": "OBE result data fetched successfully.",
            "data": {
                "sectionInfo": {
                    "sectionId": section.id,
                    "courseId": course.id,
                    "courseName": course.name,
                    "faculty": {
                        "facultyId": faculty.id if faculty else None,
                        "facultyName": faculty.get_full_name() if faculty else "Not Assigned"
                    }
                },
                "CLOs": final_clo_data
            }
        }

        return Response(response_data)
