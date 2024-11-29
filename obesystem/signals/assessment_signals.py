from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from guardian.shortcuts import assign_perm, remove_perm
from obesystem.models import Assessment

@receiver(post_save, sender=Assessment)
def assign_permissions_for_assessment(sender, instance, created, **kwargs):
    """
    Assign permissions when an Assessment is created.
    """
    if created:
        # Assign CRUD permissions to the faculty for the assessment
        faculty_user = instance.section.faculty
        if faculty_user:
            assign_perm('obesystem.add_assessment', faculty_user, instance)
            assign_perm('obesystem.view_assessment', faculty_user, instance)
            assign_perm('obesystem.change_assessment', faculty_user, instance)
            assign_perm('obesystem.delete_assessment', faculty_user, instance)

        # Assign view permissions to students for the assessment
        students = instance.section.students.all()
        for student in students:
            assign_perm('obesystem.view_assessment', student, instance)

@receiver(post_delete, sender=Assessment)
def remove_permissions_for_assessment(sender, instance, **kwargs):
    """
    Remove permissions when an Assessment is deleted.
    """
    # Remove faculty permissions
    faculty_user = instance.section.faculty
    if faculty_user:
        remove_perm('obesystem.add_assessment', faculty_user, instance)
        remove_perm('obesystem.view_assessment', faculty_user, instance)
        remove_perm('obesystem.change_assessment', faculty_user, instance)
        remove_perm('obesystem.delete_assessment', faculty_user, instance)

    # Remove student permissions
    students = instance.section.students.all()
    for student in students:
        remove_perm('obesystem.view_assessment', student, instance)