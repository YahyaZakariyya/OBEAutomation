from obesystem.models import CourseLearningOutcome, ProgramLearningOutcome, StudentQuestionScore, ProgramCLOMapping

from decimal import Decimal

def calculate_clo_attainment(clo, student_id):
    # Retrieve all questions linked to the CLO
    print([Decimal(question.marks) for question in clo.questions.all()])
    total_marks = sum(Decimal(question.marks) for question in clo.questions.all())
    print([Decimal(score.marks_obtained)
        for score in StudentQuestionScore.objects.filter(question__clo=clo, student_id=student_id)])
    obtained_marks = sum(
        Decimal(score.marks_obtained)
        for score in StudentQuestionScore.objects.filter(question__clo=clo, student_id=student_id)
    )

    # Convert clo.weightage to Decimal to ensure compatibility
    weightage = Decimal(clo.weightage)
    print(weightage)

    # Calculate attainment
    return (obtained_marks / total_marks) * weightage if total_marks > 0 else 0


def calculate_plo_attainment(plo, student_id):
    # Get all CLOs mapped to the PLO
    mappings = ProgramCLOMapping.objects.filter(plo=plo)
    total_weighted_attainment = 0
    total_weightage = 0

    for mapping in mappings:
        clo_attainment = calculate_clo_attainment(mapping.clo, student_id)
        total_weighted_attainment += clo_attainment * mapping.weightage
        total_weightage += mapping.weightage

    return total_weighted_attainment / total_weightage if total_weightage > 0 else 0
