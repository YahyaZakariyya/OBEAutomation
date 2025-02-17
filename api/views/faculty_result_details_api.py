from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from sections.models import Section
from assessments.models import Question, StudentQuestionScore
from guardian.shortcuts import get_objects_for_user

class FacultyResultDetailsAPI(APIView):
    def get(self, request, section_id):
        # Parse filters
        assessment_type = request.query_params.get('assessment_type')
        assessment_id = request.query_params.get('assessment_id')
        show_students = request.query_params.get('show_students', 'false').lower() == 'true'

        # Validate section
        faculty = request.user
        faculty_sections = get_objects_for_user(faculty, 'view_section', Section)
        section = get_object_or_404(faculty_sections, id=section_id)

        breakdown = section.assessmentbreakdown.get_assessment_types()

        if not assessment_type and not assessment_id:
            return self.section_overview(section, breakdown, show_students)

        if assessment_type and not assessment_id:
            return self.type_details(section, breakdown, assessment_type, show_students)

        if assessment_type and assessment_id:
            return self.assessment_details(section, assessment_type, assessment_id, show_students)

        return Response({"error": "Invalid parameters"}, status=400)


    def section_overview(self, section, breakdown, show_students):
        assessment_types_data = []
        students = section.students.all()
        student_scores = {student.id: {
            "student_id": student.id,
            "student_name": student.get_full_name(),
            "assessment_type_score": {},
            "total_score": 0,
            "percentage": 0,
            "adjusted_course_score": 0,
        } for student in students}

        # Pre-compute data for all assessment types
        for assessment_type, weight in breakdown.items():
            if weight == 0:
                continue
            assessments = section.assessments.filter(type=assessment_type)
            total_type_marks = 0
            total_type_weightage = 0  # To sum up the weightage of all assessments of this type
            student_total_marks = {student.id: 0 for student in students}  # Total marks for each student

            for assessment in assessments:
                questions = Question.objects.filter(assessment=assessment)
                total_type_marks += sum(q.marks for q in questions)
                total_type_weightage += assessment.weightage  # Summing up weightage for this type

                for student in students:
                    student_total_marks[student.id] += sum(
                        StudentQuestionScore.objects.filter(
                            student=student, question__in=questions
                        ).values_list('marks_obtained', flat=True)
                    )

            # Calculate highest, lowest, and average marks for this type
            all_student_marks = list(student_total_marks.values())
            average = sum(all_student_marks) / len(all_student_marks) if all_student_marks else 0
            highest = max(all_student_marks) if all_student_marks else 0
            lowest = min(all_student_marks) if all_student_marks else 0

            # Calculate completion percentage for this type
            completion_percentage = (total_type_weightage / 100) * weight if weight > 0 else 0

            assessment_types_data.append({
                "type": assessment_type,
                "assessment_count": len(assessments),
                "allocated_weight": weight,
                "total_type_marks": total_type_marks,
                "completion_percentage": round(completion_percentage, 2),
                "average": round(average, 2),
                "highest": highest,
                "lowest": lowest,
            })

            # Update student_scores for this assessment type
            for student in students:
                obtained_score = student_total_marks[student.id]
                adjusted_score = (
                    (float(obtained_score) / total_type_marks) * completion_percentage
                    if total_type_marks > 0 else 0
                )
                student_scores[student.id]["assessment_type_score"][assessment_type] = {
                    "obtained_score": obtained_score,
                    "adjusted_score": round(adjusted_score, 2),
                }
                student_scores[student.id]["total_score"] += obtained_score
                student_scores[student.id]["adjusted_course_score"] += adjusted_score

        # Aggregate section-level performance
        total_marks = sum(q.marks for q in Question.objects.filter(assessment__section=section))
        for student_id, student_data in student_scores.items():
            student_data["percentage"] = round(
                (float(student_data["total_score"]) / total_marks) * 100, 2
            ) if total_marks > 0 else 0

        response_data = {
            "section_id": section.id,
            "course_completion": sum(
                at["completion_percentage"] for at in assessment_types_data
            ),
            "student_performance": {
                "average": round(
                    sum([s["percentage"] for s in student_scores.values()]) / len(student_scores), 2
                ) if student_scores else 0,
                "highest": max([s["percentage"] for s in student_scores.values()]) if student_scores else 0,
                "lowest": min([s["percentage"] for s in student_scores.values()]) if student_scores else 0,
            },
            "assessment_types": assessment_types_data,
        }

        # Include student breakdown if requested
        if show_students:
            response_data["students"] = list(student_scores.values())

        return Response(response_data)

    def type_details(self, section, breakdown, assessment_type, show_students):
        assessments = section.assessments.filter(type=assessment_type)
        weight = breakdown.get(assessment_type, 0)
        students = section.students.all()

        # Prepare data for each assessment
        assessments_data = []
        total_type_marks = 0  # Track total marks for this type

        for assessment in assessments:
            questions = Question.objects.filter(assessment=assessment)
            total_marks = sum(q.marks for q in questions)
            total_type_marks += total_marks  # Accumulate total marks for all assessments of this type

            scores = []
            for student in students:
                obtained_marks = sum(
                    StudentQuestionScore.objects.filter(
                        student=student, question__in=questions
                    ).values_list('marks_obtained', flat=True)
                )
                scores.append(obtained_marks)

            # Correct adjusted_total_marks calculation
            assessment_weightage = assessment.weightage
            adjusted_total_marks = (assessment_weightage / 100) * weight

            assessments_data.append({
                "assessment_id": assessment.id,
                "title": assessment.title,
                "total_marks": total_marks,
                "average": round(sum(scores) / len(scores), 2) if scores else 0,
                "highest": max(scores) if scores else 0,
                "lowest": min(scores) if scores else 0,
                "assessment_weightage": assessment_weightage,
                "adjusted_total_marks": round(adjusted_total_marks, 2)
            })

        response_data = {
            "section_id": section.id,
            "assessment_type": assessment_type,
            "type_allocated_weight": weight,
            "assessments": assessments_data,
        }

        # Include student breakdown if requested
        if show_students:
            student_data = []
            for student in students:
                student_score = 0
                assessment_details = {}

                for assessment in assessments:
                    questions = Question.objects.filter(assessment=assessment)
                    obtained_marks = sum(
                        StudentQuestionScore.objects.filter(
                            student=student, question__in=questions
                        ).values_list('marks_obtained', flat=True)
                    )
                    total_marks = sum(q.marks for q in questions)

                    # Correct adjusted score calculations
                    adjusted_total_marks = (assessment.weightage / 100) * weight
                    obtained_adjusted_score = (
                        (float(obtained_marks) / total_marks) * adjusted_total_marks
                        if total_marks > 0 else 0
                    )

                    assessment_details[assessment.id] = {
                        "assessment_title": assessment.title,
                        "obtained_marks": obtained_marks,
                        "total_marks": total_marks,
                        "percentage": round(
                            (float(obtained_marks) / total_marks) * 100, 2
                        ) if total_marks > 0 else 0,
                        "adjusted_total_marks": round(adjusted_total_marks, 2),
                        "obtained_adjusted_score": round(obtained_adjusted_score, 2),
                    }
                    student_score += obtained_marks

                student_data.append({
                    "student_id": student.id,
                    "student_name": student.get_full_name(),
                    "type_score": student_score,
                    "percentage": round(
                        (float(student_score) / total_type_marks) * 100, 2
                    ) if total_type_marks > 0 else 0,
                    "assessment_details": assessment_details,
                })

            response_data["students"] = student_data

        return Response(response_data)