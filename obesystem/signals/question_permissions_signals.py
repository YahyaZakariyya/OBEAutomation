from django.db.models.signals import post_save
from django.dispatch import receiver
from guardian.shortcuts import assign_perm

from obesystem.models import Question

@receiver(post_save, sender=Question)
def configure_question_permissions(sender, instance, created, **kwargs):
    """
    Assign object-level permissions when a question is created.
    """
    if created:
        assessment = instance.assessment  # Fetch the related assessment
        section = assessment.section  # Fetch the related section
        faculty = section.faculty  # Fetch the faculty member of the section
        students = section.students.all()  # Fetch the students of the section

        # Assign permissions to the faculty member
        if faculty:
            assign_perm('obesystem.view_question', faculty, instance)
            assign_perm('obesystem.change_question', faculty, instance)
            assign_perm('obesystem.delete_question', faculty, instance)

        # Assign view permissions to the students
        for student in students:
            assign_perm('obesystem.view_question', student, instance)
