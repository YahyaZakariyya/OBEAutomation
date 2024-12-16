from django.db.models import Sum, F
from assessments.models import Assessment, Question, StudentQuestionScore
from outcomes.models import CourseLearningOutcome

def compute_clo_attainment(student, section, assessment_type=None):
    # Filter assessments for the section (and optionally by type)
    assessments = Assessment.objects.filter(section=section)
    if assessment_type:
        assessments = assessments.filter(type=assessment_type)

    # Get questions linked to these assessments
    questions = Question.objects.filter(assessment__in=assessments).prefetch_related('clo')

    # Get all CLOs for the course associated with the section
    all_clos = CourseLearningOutcome.objects.filter(course=section.course)

    # Initialize a CLO dictionary for all CLOs (ensures unused CLOs are included)
    clo_data = {clo.id: {'name': clo.heading, 'obtained': 0, 'total': 0} for clo in all_clos}

    # Populate CLO dictionary with question data
    for question in questions:
        for clo in question.clo.all():
            clo_data[clo.id]['total'] += question.marks

    # Retrieve student scores for the questions
    scores = StudentQuestionScore.objects.filter(student=student, question__in=questions)

    for score in scores:
        for clo in score.question.clo.all():
            clo_data[clo.id]['obtained'] += score.marks_obtained

    # Compute attainment percentages and prepare the result
    result = []
    for clo_id, data in clo_data.items():
        percentage = (float(data['obtained']) / float(data['total'])) * 100 if data['total'] > 0 else 0
        result.append({
            'clo_id': clo_id,
            'clo_name': data['name'],
            'total_marks': float(data['total']),
            'obtained_marks': float(data['obtained']),
            'attainment': round(percentage, 2)
        })

    return result
