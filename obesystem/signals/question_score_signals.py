from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from obesystem.models import Question, StudentQuestionScore

@receiver(post_save, sender=Question)
def create_student_scores(sender, instance, created, **kwargs):
    if created:
        # Get all students enrolled in the section of the related assessment
        students = instance.assessment.section.students.all()  # Assuming section.students is a ManyToManyField
        for student in students:
            StudentQuestionScore.objects.create(
                student=student,
                question=instance,
                marks_obtained=0.0  # Default marks
            )

@receiver(post_delete, sender=Question)
def delete_student_scores(sender, instance, **kwargs):
    StudentQuestionScore.objects.filter(question=instance).delete()