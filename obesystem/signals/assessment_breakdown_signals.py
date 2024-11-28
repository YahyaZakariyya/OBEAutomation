from django.db.models.signals import post_save
from django.dispatch import receiver
from guardian.shortcuts import assign_perm
from obesystem.models import AssessmentBreakdown

@receiver(post_save, sender=AssessmentBreakdown)
def assign_permissions_for_assessment_breakdown(sender, instance, created, **kwargs):
    """
    Assign permissions for a newly created AssessmentBreakdown.
    """
    if created and instance.section:
        faculty_user = instance.section.faculty
        if faculty_user:
            # Assign permissions to the faculty for the new assessment breakdown
            assign_perm('obesystem.view_assessmentbreakdown', faculty_user, instance)
            assign_perm('obesystem.change_assessmentbreakdown', faculty_user, instance)

        # Assign view permission to students of the section
        students = instance.section.students.all()
        for student in students:
            assign_perm('obesystem.view_assessmentbreakdown', student, instance)