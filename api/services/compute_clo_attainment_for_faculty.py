from django.db.models import Sum
from obesystem.models import Assessment, Question, StudentQuestionScore, CourseLearningOutcome

def compute_clo_attainment_for_faculty(faculty_user, section, assessment_type=None):
    # Validate that faculty_user teaches the section
    if section.faculty != faculty_user:
        raise PermissionError("You are not assigned to this section.")

    # Get enrolled students
    enrolled_students = section.students.all()
    if not enrolled_students:
        return {
            "section_id": section.id,
            "clo_average_attainments": [],
            "students_data": []
        }

    # Filter assessments
    assessments = section.assessments.all()
    if assessment_type:
        assessments = assessments.filter(type=assessment_type)

    # Get questions and CLOs
    questions = Question.objects.filter(assessment__in=assessments).prefetch_related('clo')
    all_clos = CourseLearningOutcome.objects.filter(course=section.course)

    # Initialize CLO data structure
    clo_data = {clo.id: {'name': clo.heading, 'students': {s.id: {'obtained': 0, 'total': 0} for s in enrolled_students}} for clo in all_clos}

    # Populate question data
    for question in questions:
        for clo in question.clo.all():
            for student in enrolled_students:
                clo_data[clo.id]['students'][student.id]['total'] += question.marks

    # Get student scores
    scores = StudentQuestionScore.objects.filter(student__in=enrolled_students, question__in=questions)

    for score in scores:
        for clo in score.question.clo.all():
            clo_data[clo.id]['students'][score.student.id]['obtained'] += score.marks_obtained

    # Compute aggregated and student-level CLO attainments
    clo_average_attainments = []
    student_map = {s.id: {'student_id': s.id, 'student_name': s.get_full_name(), 'clo_attainments': []} for s in enrolled_students}

    for clo_id, data in clo_data.items():
        total_percentage_sum = 0
        student_count = len(enrolled_students)

        for student_id, marks_data in data['students'].items():
            percentage = (float(marks_data['obtained']) / float(marks_data['total'])) * 100 if marks_data['total'] > 0 else 0
            total_percentage_sum += percentage
            student_map[student_id]['clo_attainments'].append({
                'clo_id': clo_id,
                'clo_name': data['name'],
                'obtained_percentage': round(percentage, 2)
            })

        average_percentage = round(total_percentage_sum / student_count, 2) if student_count > 0 else 0
        clo_average_attainments.append({
            'clo_id': clo_id,
            'clo_name': data['name'],
            'average_percentage': average_percentage
        })

    # Convert student map to list
    students_data = list(student_map.values())

    return {
        "section_id": section.id,
        "clo_average_attainments": clo_average_attainments,
        "students_data": students_data
    }
