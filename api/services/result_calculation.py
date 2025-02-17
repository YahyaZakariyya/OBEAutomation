from django.db.models import Sum
from sections.models import Section
from assessments.models import Assessment, Question, StudentQuestionScore
from outcomes.models import CourseLearningOutcome

def calculate_student_results(section_id, student_id):
    # Retrieve the section and student
    section = Section.objects.get(id=section_id)
    student = section.students.get(id=student_id)

    # Retrieve the assessment breakdown for the section
    assessment_breakdown = section.assessmentbreakdown

    result = {
        "section_id": section.id,
        "student_id": student.id,
        "total_weight": 100.0,
        "course_completion": 0.0,
        "student_current_overall": 0.0,
        "assessment_types": [],
        "clo_based_results": []
    }

    overall_completion = 0.0
    overall_score = 0.0

    # Iterate over all assessment types in the breakdown
    for assessment_type, allocated_weight in assessment_breakdown.get_assessment_types().items():
        if allocated_weight == 0:
            continue
        # Initialize cumulative variables for this type
        total_marks_sum = 0.0
        obtained_marks_sum = 0.0
        assessment_weight_sum = 0.0
        assessment_type_assessments = []

        # Retrieve and process assessments of the current type
        assessments = Assessment.objects.filter(section=section, type=assessment_type)
        for assessment in assessments:
            questions = assessment.questions.all()
            total_marks = questions.aggregate(total=Sum("marks"))["total"] or 0.0
            obtained_marks = StudentQuestionScore.objects.filter(student=student, question__in=questions).aggregate(obtained=Sum("marks_obtained"))["obtained"] or 0.0
            assessment_weight = assessment.weightage

            # Adjusted marks for this assessment
            adjusted_marks = (float(obtained_marks) / total_marks) * assessment_weight if total_marks > 0 else 0.0

            # Update cumulative values
            total_marks_sum += total_marks
            obtained_marks_sum += float(obtained_marks)
            assessment_weight_sum += assessment_weight

            # Question details
            question_details = [
                {
                    "question_id": question.id,
                    "marks": question.marks,
                    "obtained_marks": StudentQuestionScore.objects.filter(student=student, question=question).first().marks_obtained or 0.0,
                    "percentage": float(StudentQuestionScore.objects.filter(student=student, question=question).first().marks_obtained or 0.0) / question.marks * 100 if question.marks > 0 else 0.0
                }
                for question in questions
            ]

            # Append assessment data
            assessment_type_assessments.append({
                "assessment_id": assessment.id,
                "title": assessment.title,
                "total_marks": total_marks,
                "student_obtained_marks": obtained_marks,
                "assessment_weight": assessment_weight,
                "adjusted_marks": adjusted_marks,
                "percentage": (float(obtained_marks)/total_marks)*100 if total_marks > 0 else 0.0,
                "questions": question_details
            })

        # Calculate completion percentage for this type
        completion_percentage = (float(assessment_weight_sum) / 100) * allocated_weight if allocated_weight > 0 else 0.0

        # Calculate student's earned percentage for this type
        student_earned_percentage = (float(obtained_marks_sum) / total_marks_sum) * 100 if total_marks_sum > 0 else 0.0

        # Append assessment type data
        result["assessment_types"].append({
            "type": assessment_type,
            "allocated_weight": allocated_weight,
            "completion_percentage": completion_percentage,
            "student_earned_percentage": student_earned_percentage,
            "total_marks": total_marks_sum,
            "obtained_marks": obtained_marks_sum,
            "adjusted_marks": (student_earned_percentage/100) * allocated_weight,
            "assessments": assessment_type_assessments
        })

        # Update overall metrics
        overall_completion += completion_percentage
        overall_score += ((student_earned_percentage/100) * allocated_weight)

    result["course_completion"] = overall_completion
    result["student_current_overall"] = overall_score

    # CLO-based results
    clos = CourseLearningOutcome.objects.filter(course=section.course)
    clo_results = []
    for clo in clos:
        questions = Question.objects.filter(clo=clo, assessment__section=section)
        total_marks = questions.aggregate(total=Sum("marks"))["total"] or 0.0
        obtained_marks = StudentQuestionScore.objects.filter(student=student, question__in=questions).aggregate(obtained=Sum("marks_obtained"))["obtained"] or 0.0
        percentage = (float(obtained_marks) / total_marks) * 100 if total_marks > 0 else 0.0
        clo_results.append({
            "clo_id": clo.id,
            "clo_name": clo.heading,
            "obtained_percentage": percentage
        })
    result["clo_based_results"] = clo_results

    return result