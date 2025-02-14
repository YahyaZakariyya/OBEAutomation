from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from assessments.models import Assessment, Question, StudentQuestionScore
from sections.models import Section
from outcomes.models import CourseLearningOutcome
from assessments.models import AssessmentBreakdown


class FacultyCLOAttainmentAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, section_id):
        """
        Fully corrected API to fetch student-wise CLO attainment,
        ensuring only contributing assessments are included.
        """
        # Get Section
        section = get_object_or_404(Section, id=section_id)
        students = section.students.all()

        # Get CLOs and map by ID (Ensure ordered CLOs)
        clos = CourseLearningOutcome.objects.filter(course=section.course).order_by("CLO")
        clo_mapping = {clo.id: f"CLO{clo.CLO}" for clo in clos}

        # Get Assessment Breakdown (for weightages)
        breakdown = AssessmentBreakdown.objects.filter(section=section).first()
        if not breakdown:
            return Response({"status": "error", "message": "Assessment Breakdown not found"}, status=404)

        assessment_weights = breakdown.get_assessment_types()  # Fetch dynamic weightages

        # Exclude assessments with 0 weightage
        valid_assessment_types = {atype: weight for atype, weight in assessment_weights.items() if weight > 0}

        # Get Assessments and Questions
        assessments = Assessment.objects.filter(section=section, type__in=valid_assessment_types.keys()).prefetch_related("questions")
        questions = Question.objects.filter(assessment__section=section).prefetch_related("clo")
        student_scores = StudentQuestionScore.objects.filter(question__assessment__section=section)

        # **Data Structure Initialization**
        clo_results = {
            clo_mapping[clo.id]: {
                "title": clo.heading,
                "weightage": clo.weightage,
                "totalMarks": 0,
                "assessmentTypeContribution": {}
            }
            for clo in clos
        }

        student_results = {
            student.get_full_name(): {
                clo_key: {}  # Only add assessments if they contribute
                for clo_key in clo_mapping.values()
            }
            for student in students
        }

        # **Process Data**
        for assessment in assessments:
            total_assessment_marks = sum(q.marks for q in assessment.questions.all())
            if total_assessment_marks == 0:
                continue  # Skip empty assessments

            assessment_type = assessment.type
            effective_weight = valid_assessment_types[assessment.type]
            adjusted_weight = effective_weight*assessment.weightage/100

            for question in assessment.questions.all():
                if not question.clo.exists():
                    continue  # Skip questions without CLOs

                question_weight = (question.marks / total_assessment_marks) * adjusted_weight
                mapped_clos = question.clo.all()
                num_clos = mapped_clos.count()

                for clo in mapped_clos:
                    distributed_weight = question_weight / num_clos
                    clo_key = clo_mapping[clo.id]
                    clo_results[clo_key]["totalMarks"] += distributed_weight

                    # Add assessment type only if it contributes
                    if assessment_type not in clo_results[clo_key]["assessmentTypeContribution"]:
                        clo_results[clo_key]["assessmentTypeContribution"][assessment_type] = 0
                    clo_results[clo_key]["assessmentTypeContribution"][assessment_type] += distributed_weight
                    print('Assessment Type:',assessment_type, clo_results[clo_key]["assessmentTypeContribution"][assessment_type])

                    # Add student results, but only for relevant CLOs
                    for student in students:
                        student_name = student.get_full_name()
                        score = student_scores.filter(student=student, question=question).first()
                        if score:
                            student_results[student_name][clo_key].setdefault(assessment_type, 0)
                            student_results[student_name][clo_key][assessment_type] += (
                                (score.marks_obtained / question.marks) * distributed_weight
                            )

        # # **Convert CLO contribution to percentage**
        # for clo_key, clo_data in clo_results.items():
        #     total_contribution = sum(clo_data["assessmentTypeContribution"].values())
        #     if total_contribution > 0:
        #         for key in clo_data["assessmentTypeContribution"]:
        #             clo_data["assessmentTypeContribution"][key] = (
        #                 clo_data["assessmentTypeContribution"][key] / total_contribution
        #             ) * 100

        # **Prepare Final JSON Response**
        response_data = {
            "status": "success",
            "message": "OBE result data fetched successfully.",
            "data": {
                "CLOs": list(clo_results.values()),  # CLOs are now properly structured
                "students": student_results  # Each student now matches the CLO hierarchy
            }
        }

        return Response(response_data)
