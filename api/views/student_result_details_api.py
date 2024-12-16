from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from sections.models import Section
from assessments.models import Assessment, Question, StudentQuestionScore


class StudentResultDetailsAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, section_id):
        # Filters from the request
        assessment_type = request.query_params.get('assessment_type')
        assessment_id = request.query_params.get('assessment_id')

        # Validate section and fetch its breakdown
        student = request.user
        section = get_object_or_404(Section, id=section_id, students=student)
        breakdown = section.assessmentbreakdown.get_assessment_types()

        # Level 1: Section Overview
        if not assessment_type and not assessment_id:
            return self.section_overview(section, breakdown, student)

        # Level 2: Assessment Type Details
        if assessment_type and not assessment_id:
            return self.type_details(section, breakdown, student, assessment_type)

        # Level 3: Assessment Details
        if assessment_type and assessment_id:
            return self.assessment_details(section, student, assessment_type, assessment_id)

        return Response({"error": "Invalid request parameters."}, status=400)

    def section_overview(self, section, breakdown, student):
        # Calculate overall course completion and student performance
        total_completion = 0
        student_performance = 0
        assessment_types_data = []

        for assessment_type, weight in breakdown.items():
            assessments = section.assessments.filter(type=assessment_type)
            total_assessments_weightage = sum(a.weightage for a in assessments)

            completion_percentage = (total_assessments_weightage / 100) * weight if weight > 0 else 0
            total_completion += completion_percentage

            # Calculate student's performance for this type
            type_total_marks = 0
            type_obtained_marks = 0
            for assessment in assessments:
                questions = Question.objects.filter(assessment=assessment)
                type_total_marks += sum(q.marks for q in questions)
                type_obtained_marks += sum(
                    StudentQuestionScore.objects.filter(student=student, question__in=questions)
                    .values_list('marks_obtained', flat=True)
                )

            student_performance_in_type = (
                (float(type_obtained_marks) / type_total_marks) * (completion_percentage / 100) * weight
                if type_total_marks > 0
                else 0
            )
            student_performance += student_performance_in_type

            assessment_types_data.append({
                "type": assessment_type,
                "allocated_weight": weight,
                "completion_percentage": round(completion_percentage, 2),
                "student_earned_percentage_of_this_type": round(student_performance_in_type, 2),
            })

        return Response({
            "section_id": section.id,
            "total_weight": 100,
            "course_completion": round(total_completion, 2),
            "student_current_overall": round(student_performance, 2),
            "assessment_types": assessment_types_data,
        })

    def type_details(self, section, breakdown, student, assessment_type):
        weight = breakdown.get(assessment_type, 0)
        assessments = section.assessments.filter(type=assessment_type)

        type_total_marks = 0
        type_obtained_marks = 0
        assessments_data = []

        for assessment in assessments:
            questions = Question.objects.filter(assessment=assessment)
            assessment_total_marks = sum(q.marks for q in questions)
            assessment_obtained_marks = sum(
                StudentQuestionScore.objects.filter(student=student, question__in=questions)
                .values_list('marks_obtained', flat=True)
            )

            assessment_percentage = (
                (float(assessment_obtained_marks) / assessment_total_marks) * 100 if assessment_total_marks > 0 else 0
            )
            weighted_contribution = (assessment_percentage * weight) / 100

            assessments_data.append({
                "assessment_id": assessment.id,
                "title": assessment.title,
                "total_marks": assessment_total_marks,
                "student_obtained_marks": assessment_obtained_marks,
                "assessment_percentage": round(assessment_percentage, 2),
                "weighted_contribution": round(weighted_contribution, 2),
            })

            type_total_marks += assessment_total_marks
            type_obtained_marks += assessment_obtained_marks

        type_completion_percentage = (
            (sum(a.weightage for a in assessments) / 100) * weight if weight > 0 else 0
        )
        student_type_percentage = (
            (float(type_obtained_marks) / type_total_marks) * (type_completion_percentage / 100) * weight
            if type_total_marks > 0
            else 0
        )

        return Response({
            "section_id": section.id,
            "assessment_type": assessment_type,
            "type_allocated_weight": weight,
            "type_completion_percentage": round(type_completion_percentage, 2),
            "student_type_percentage": round(student_type_percentage, 2),
            "assessments": assessments_data,
        })

    def assessment_details(self, section, student, assessment_type, assessment_id):
        assessment = get_object_or_404(Assessment, id=assessment_id, section=section, type=assessment_type)
        questions = Question.objects.filter(assessment=assessment)

        assessment_total_marks = sum(q.marks for q in questions)
        assessment_obtained_marks = sum(
            StudentQuestionScore.objects.filter(student=student, question__in=questions)
            .values_list('marks_obtained', flat=True)
        )

        questions_data = []
        for question in questions:
            obtained_marks = StudentQuestionScore.objects.filter(student=student, question=question).first()
            obtained_marks = obtained_marks.marks_obtained if obtained_marks else 0
            question_percentage = (float(obtained_marks) / question.marks) * 100 if question.marks > 0 else 0

            questions_data.append({
                "question_id": question.id,
                # "question_title": question.title,
                "total_marks": question.marks,
                "student_obtained_marks": obtained_marks,
                "question_percentage": round(question_percentage, 2),
            })

        assessment_percentage = (
            (float(assessment_obtained_marks) / assessment_total_marks) * 100 if assessment_total_marks > 0 else 0
        )

        return Response({
            "section_id": section.id,
            "assessment_type": assessment_type,
            "assessment_id": assessment.id,
            "title": assessment.title,
            "total_marks": assessment_total_marks,
            "student_obtained_marks": assessment_obtained_marks,
            "assessment_percentage": round(assessment_percentage, 2),
            "questions": questions_data,
        })