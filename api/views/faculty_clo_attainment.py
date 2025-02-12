from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum
from assessments.models import Assessment, Question, StudentQuestionScore
from sections.models import Section
from outcomes.models import CourseLearningOutcome
from assessments.models import AssessmentBreakdown


class FacultyCLOAttainment(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, section_id):
        """
        API to fetch OBE result details for a given section.
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

        # Mapping CLO IDs for faster lookup
        clo_lookup = {
            clo.id: {
                "cloCode": f"CLO{clo.CLO}",
                "title": clo.heading,
                "weightage": clo.weightage,
                "totalMarks": 0,
                "studentAttainment": {}
            }
            for clo in clos
        }

        # Get All Assessments for the Section
        assessments = Assessment.objects.filter(section=section)
        assessment_data = []

        for assessment in assessments:
            assessment_category_weightage = assessment_weights.get(assessment.type, 0)  # e.g., Assignments = 15%
            effectiveAssessmentWeightage = (assessment.weightage / 100) * assessment_category_weightage  # Corrected calculation

            assessment_info = {
                "assessmentId": assessment.id,
                "assessmentTitle": assessment.title,
                "assessmentType": assessment.type,
                "assessmentWeightage": assessment.weightage,
                "effectiveAssessmentWeightage": round(effectiveAssessmentWeightage, 2),
                "questions": []
            }

            # Get all Questions under this Assessment
            questions = Question.objects.filter(assessment=assessment)
            total_question_marks = sum(q.marks for q in questions)  # Total marks across all questions

            for question in questions:
                normalized_question_weight = (question.marks / total_question_marks) * effectiveAssessmentWeightage  # Proper scaling

                question_info = {
                    "questionId": question.id,
                    "totalMarks": question.marks,
                    "normalizedMarks": round(normalized_question_weight, 2),
                    "mappedCLOs": [],
                    "studentScores": []
                }

                # Get CLOs mapped to this question
                mapped_clos = question.clo.all()
                num_clos = mapped_clos.count()

                for clo in mapped_clos:
                    distribution_factor = 1 / num_clos  # If mapped to multiple CLOs, distribute marks equally
                    question_info["mappedCLOs"].append({
                        "cloId": clo.id,
                        "cloCode": f"CLO{clo.CLO}",
                        "distributionFactor": round(distribution_factor, 2)
                    })

                # Get Student Scores for this Question
                student_scores = StudentQuestionScore.objects.filter(question=question)

                for score in student_scores:
                    student_id = int(score.student.id)  # Ensure student_id is always an integer
                    obtained_marks = float(score.marks_obtained)  # Convert to float for calculations
                    converted_marks = (obtained_marks / question.marks) * normalized_question_weight  # Corrected student score calculation

                    student_data = {
                        "studentId": student_id,
                        "studentName": score.student.get_full_name(),
                        "obtainedMarks": obtained_marks,
                        "convertedMarks": round(converted_marks, 2)
                    }

                    question_info["studentScores"].append(student_data)

                    # Ensure student ID is stored correctly in CLO attainment
                    for clo in mapped_clos:
                        if student_id not in clo_lookup[clo.id]["studentAttainment"]:
                            clo_lookup[clo.id]["studentAttainment"][student_id] = 0  # Initialize with 0

                        clo_lookup[clo.id]["studentAttainment"][student_id] += round(converted_marks * (1 / num_clos), 2)

                assessment_info["questions"].append(question_info)

            assessment_data.append(assessment_info)

        # Final CLO Calculation
        final_clo_data = []
        for clo_id, clo_info in clo_lookup.items():
            total_clo_marks = sum(clo_info["studentAttainment"].values())
            avg_attainment = total_clo_marks / max(1, len(clo_info["studentAttainment"]))  # Avoid division by zero
            clo_info["totalMarks"] = round(total_clo_marks, 2)
            clo_info["averageAttainment"] = round(avg_attainment, 2)

            # Convert student attainment dictionary into a list format
            clo_info["studentsAttainment"] = [
                {
                    "studentId": sid,
                    "obtainedCLOMarks": round(marks, 2),
                    "convertedPercentage": round((marks / clo_info["totalMarks"]) * 100 if clo_info["totalMarks"] > 0 else 0, 2)
                }
                for sid, marks in clo_info["studentAttainment"].items()
            ]

            del clo_info["studentAttainment"]
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
                "CLOs": final_clo_data,
                "assessmentBreakdown": assessment_data
            }
        }

        return Response(response_data)
