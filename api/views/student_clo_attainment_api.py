from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from assessments.models import Question, StudentQuestionScore
from sections.models import Section
from outcomes.models import CourseLearningOutcome
from django.shortcuts import get_object_or_404


class StudentCLOAttainmentAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, section_id, student_id):
        """
        API to fetch detailed OBE result for a specific student.
        """

        # Get Section
        section = get_object_or_404(Section, id=section_id)

        # Get all CLOs for the Course
        clos = CourseLearningOutcome.objects.filter(course=section.course)

        # CLO Data Structure
        clo_data = {
            clo.id: {
                "cloCode": f"CLO{clo.CLO}",
                "title": clo.heading,
                "weightage": clo.weightage,
                "totalMarks": 0,
                "studentScore": 0,
                "questions": []
            }
            for clo in clos
        }

        # Get All Questions Attempted by Student
        student_scores = StudentQuestionScore.objects.filter(student_id=student_id, question__assessment__section=section)

        for score in student_scores:
            question = score.question
            obtained_marks = float(score.marks_obtained)
            total_marks = float(question.marks)

            question_info = {
                "questionId": question.id,
                "totalMarks": question.marks,
                "obtainedMarks": obtained_marks,
                "normalizedScore": round((obtained_marks / total_marks) * 100, 2),
                "mappedCLOs": []
            }

            # Get CLOs for the Question
            mapped_clos = question.clo.all()
            num_clos = mapped_clos.count()

            for clo in mapped_clos:
                distribution_factor = 1 / num_clos
                clo_data[clo.id]["totalMarks"] += question.marks * distribution_factor
                clo_data[clo.id]["studentScore"] += obtained_marks * distribution_factor

                question_info["mappedCLOs"].append({
                    "cloId": clo.id,
                    "cloCode": f"CLO{clo.CLO}",
                    "distributionFactor": round(distribution_factor, 2)
                })

            clo_data[clo.id]["questions"].append(question_info)

        # Convert CLO Data to List Format
        response_clos = []
        for clo in clo_data.values():
            clo["finalPercentage"] = round((clo["studentScore"] / clo["totalMarks"]) * 100, 2) if clo["totalMarks"] > 0 else 0
            response_clos.append(clo)

        response_data = {
            "status": "success",
            "message": "Student OBE result fetched successfully.",
            "data": {
                "studentId": student_id,
                "sectionId": section.id,
                "CLOs": response_clos
            }
        }

        return Response(response_data)
