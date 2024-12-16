from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from guardian.shortcuts import assign_perm, remove_perm
from django.contrib.auth.models import Group
from assessments.models import Assessment

@receiver(post_save, sender=Assessment)
def assign_permissions_for_assessment(sender, instance, created, **kwargs):
    """
    Assign permissions when an Assessment is created, based on Section groups.
    """
    if created:
        # Get the faculty and students group names
        faculty_group_name = f"faculty_section_{instance.section.pk}"
        students_group_name = f"students_section_{instance.section.pk}"

        # Get the groups
        faculty_group = Group.objects.get(name=faculty_group_name)
        students_group = Group.objects.get(name=students_group_name)

        # Assign CRUD permissions to the faculty group for the assessment
        assign_perm('assessments.view_assessment', faculty_group, instance)
        assign_perm('assessments.change_assessment', faculty_group, instance)
        assign_perm('assessments.delete_assessment', faculty_group, instance)
        assign_perm('assessments.can_add_question', faculty_group, instance)

        # Assign view permissions to the students group for the assessment
        assign_perm('assessments.view_assessment', students_group, instance)

@receiver(post_delete, sender=Assessment)
def remove_permissions_for_assessment(sender, instance, **kwargs):
    """
    Remove permissions when an Assessment is deleted, based on Section groups.
    """
    # Get the faculty and students group names
    faculty_group_name = f"faculty_section_{instance.section.pk}"
    students_group_name = f"students_section_{instance.section.pk}"

    # Get the groups
    faculty_group = Group.objects.get(name=faculty_group_name)
    students_group = Group.objects.get(name=students_group_name)

    # Remove CRUD permissions for the faculty group
    remove_perm('assessments.view_assessment', faculty_group, instance)
    remove_perm('assessments.change_assessment', faculty_group, instance)
    remove_perm('assessments.delete_assessment', faculty_group, instance)
    remove_perm('assessments.can_add_question', faculty_group, instance)

    # Remove view permissions for the students group
    remove_perm('assessments.view_assessment', students_group, instance)