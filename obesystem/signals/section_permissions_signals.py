from django.db.models.signals import post_delete, m2m_changed, pre_delete, post_save
from django.dispatch import receiver
from obesystem.models import Section, AssessmentBreakdown, Assessment
from guardian.shortcuts import remove_perm, assign_perm

@receiver(post_save, sender=Section)
def configure_add_assessment_permission(sender, instance, created, **kwargs):
    """
    Assign `can_add_assessment` permission to the faculty member for Assessments related to their section.
    """
    if created:
        # Grant permission to add assessments for the new section
        if instance.faculty:
            print(f"Granting `can_add_assessment` permission to faculty: {instance.faculty}")
            assign_perm('obesystem.can_add_assessment', instance.faculty, instance)
    else:
        # Handle changes to the faculty member in an existing section
        try:
            old_faculty = Section.objects.get(pk=instance.pk).faculty  # Retrieve the original faculty member
        except Section.DoesNotExist:
            old_faculty = None

        new_faculty = instance.faculty

        # Revoke permission from the old faculty if it has changed
        if old_faculty and old_faculty != new_faculty:
            print(f"Revoking `can_add_assessment` permission from old faculty: {old_faculty}")
            remove_perm('obesystem.can_add_assessment', old_faculty, instance)

        # Grant permission to the new faculty if it has changed
        if new_faculty and old_faculty != new_faculty:
            print(f"Granting `can_add_assessment` permission to new faculty: {new_faculty}")
            assign_perm('obesystem.can_add_assessment', new_faculty, instance)

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

@receiver(post_delete, sender=Section)
def cleanup_faculty_permissions_on_section_delete(sender, instance, **kwargs):
    """
    Remove permissions for students and faculty when a Section is deleted.
    """
    # Remove permissions for faculty
    if instance.faculty:
        print(f"Removing permissions for faculty: {instance.faculty.username}")
        remove_perm('obesystem.view_section', instance.faculty, instance)
        assessment_breakdowns = AssessmentBreakdown.objects.filter(section=instance)
        for breakdown in assessment_breakdowns:
            remove_perm('obesystem.view_assessmentbreakdown', instance.faculty, breakdown)

        assessments = Assessment.objects.filter(section=instance)
        for assessment in assessments:
            remove_perm('obesystem.view_assessment', instance.faculty, assessment)
            remove_perm('obesystem.add_assessment', instance.faculty, assessment)
            remove_perm('obesystem.change_assessment', instance.faculty, assessment)
            remove_perm('obesystem.delete_assessment', instance.faculty, assessment)

    print("Permissions cleanup complete.")

@receiver(pre_delete, sender=Section)
def cleanup_students_permissions_on_section_delete(sender, instance, **kwargs):
    """
    Remove permissions for students and faculty when a Section is deleted.
    """
    
    # Remove permissions for students
    students = instance.students.all()  # Get all related students
    print(f"Students for Section {instance.id}: {students}")

    for student in students:
        print(f"Removing permissions for student: {student.username}")
        # Remove view permission for this section
        remove_perm('obesystem.view_section', student, instance)

        # Remove permissions for related AssessmentBreakdown
        assessment_breakdowns = AssessmentBreakdown.objects.filter(section=instance)
        for breakdown in assessment_breakdowns:
            remove_perm('obesystem.view_assessmentbreakdown', student, breakdown)

        # Remove permissions for related Assessments
        assessments = Assessment.objects.filter(section=instance)
        for assessment in assessments:
            remove_perm('obesystem.view_assessment', student, assessment)