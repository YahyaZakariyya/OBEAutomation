from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver
from obesystem.models import Section, AssessmentBreakdown
from guardian.shortcuts import remove_perm, assign_perm

@receiver(m2m_changed, sender=Section.students.through)
def assign_student_permissions_on_change(sender, instance, action, pk_set, **kwargs):
    """
    Assign permissions to students when they are added to a section.
    """
    if action == "post_add":  # Trigger after students are added
        students = instance.students.filter(pk__in=pk_set)
        for student in students:
            assessment_breakdowns = AssessmentBreakdown.objects.filter(section=instance)
            for breakdown in assessment_breakdowns:
                assign_perm('obesystem.view_assessmentbreakdown', student, breakdown)

@receiver(post_save, sender=Section)
def create_assessmentbreakdown(sender, instance, created, **kwargs):
    """
    Automatically create an AssessmentBreakdown when a Section is created.
    Initialize all weightage to 0 except for `final_weightage` which is set to 100%.
    """
    if created:
        AssessmentBreakdown.objects.create(
            section=instance,
            assignment_weightage=0,
            quiz_weightage=0,
            lab_weightage=0,
            mid_weightage=0,
            final_weightage=100,  # Set 100% weightage for Finals
            project_weightage=0,
        )

@receiver(post_delete, sender=Section)
def delete_assessmentbreakdown(sender, instance, **kwargs):
    """
    Automatically delete the related AssessmentBreakdown when a Section is deleted,
    and clean up permissions.
    """
    # Fetch all related AssessmentBreakdown objects
    assessment_breakdowns = AssessmentBreakdown.objects.filter(section=instance)
    
    # Clean up permissions for each AssessmentBreakdown
    for breakdown in assessment_breakdowns:
        faculty_user = instance.faculty
        if faculty_user:
            remove_perm('obesystem.view_assessmentbreakdown', faculty_user, breakdown)
            remove_perm('obesystem.change_assessmentbreakdown', faculty_user, breakdown)
        
        # Remove permissions for students
        students = instance.students.all()
        for student in students:
            remove_perm('obesystem.view_assessmentbreakdown', student, breakdown)

    # Delete related AssessmentBreakdown objects
    assessment_breakdowns.delete()

