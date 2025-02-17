from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from assessments.models import Assessment, Question, StudentQuestionScore
from sections.models import Section
from outcomes.models import CourseLearningOutcome
from assessments.models import AssessmentBreakdown

class StudentCLOAttainmentAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, section_id):
        """
        API to fetch **a single student’s** CLO attainment,
        ensuring only contributing assessments are included.
        """
        # ✅ Get Section
        section = get_object_or_404(Section, id=section_id)
        student = request.user  # ✅ Fetch only the logged-in student

        # ✅ Ensure the user is actually a student
        if not section.students.filter(id=student.id).exists():
            return Response({"status": "error", "message": "Access denied. You are not enrolled in this section."}, status=403)

        # ✅ Get CLOs mapped to this section
        clos = CourseLearningOutcome.objects.filter(course=section.course).order_by("CLO")
        clo_mapping = {clo.id: f"CLO{clo.CLO}" for clo in clos}

        # ✅ Get Assessment Breakdown (for weightages)
        breakdown = AssessmentBreakdown.objects.filter(section=section).first()
        if not breakdown:
            return Response({"status": "error", "message": "Assessment Breakdown not found"}, status=404)

        assessment_weights = breakdown.get_assessment_types()  # ✅ Fetch dynamic weightages

        # ✅ Exclude assessments with 0 weightage
        valid_assessment_types = {atype: weight for atype, weight in assessment_weights.items() if weight > 0}

        # ✅ Get Assessments and Questions
        assessments = Assessment.objects.filter(section=section, type__in=valid_assessment_types.keys()).prefetch_related("questions")
        questions = Question.objects.filter(assessment__section=section).prefetch_related("clo")
        student_scores = StudentQuestionScore.objects.filter(question__assessment__section=section, student=student)

        # ✅ **Data Structure Initialization**
        clo_results = {
            clo_mapping[clo.id]: {
                "clo_id": "CLO" + str(clo.CLO),
                "title": clo.heading,
                "weightage": clo.weightage,
                "totalMarks": 0,
                "assessmentTypeContribution": {}
            }
            for clo in clos
        }

        student_results = {
            "student_details": {
                "first_name": student.first_name,
                "last_name": student.last_name,
                "email": student.email,
                "sap_id": student.username,  # ✅ Use SAP ID
            },
            "clo_results": {
                clo_key: {}  # Only add assessments if they contribute
                for clo_key in clo_mapping.values()
            }
        }

        # ✅ **Process Data**
        for assessment in assessments:
            total_assessment_marks = sum(q.marks for q in assessment.questions.all())
            if total_assessment_marks == 0:
                continue  # Skip empty assessments

            assessment_type = assessment.type
            effective_weight = valid_assessment_types[assessment.type]
            adjusted_weight = effective_weight * assessment.weightage / 100

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

                    # ✅ Add assessment type contribution
                    if assessment_type not in clo_results[clo_key]["assessmentTypeContribution"]:
                        clo_results[clo_key]["assessmentTypeContribution"][assessment_type] = 0
                    clo_results[clo_key]["assessmentTypeContribution"][assessment_type] += distributed_weight

                    # ✅ Add student results
                    score = student_scores.filter(question=question).first()
                    if score:
                        student_results["clo_results"].setdefault(clo_key, {})
                        student_results["clo_results"][clo_key].setdefault(assessment_type, 0)
                        student_results["clo_results"][clo_key][assessment_type] += (
                            (score.marks_obtained / question.marks) * distributed_weight
                        )

        # ✅ **Prepare Final JSON Response**
        response_data = {
            "status": "success",
            "message": "Student OBE result data fetched successfully.",
            "data": {
                "CLOs": list(clo_results.values()),  # ✅ CLOs structured properly
                "student": student_results  # ✅ Student data properly nested
            }
        }

        return Response(response_data)
