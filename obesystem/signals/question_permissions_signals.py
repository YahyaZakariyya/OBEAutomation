from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from guardian.shortcuts import assign_perm, remove_perm
from django.contrib.auth.models import Group
from obesystem.models import Question

@receiver(post_save, sender=Question)
def configure_question_permissions(sender, instance, created, **kwargs):
    """
    Assign object-level permissions when a question is created.
    """
    if created:
        assessment = instance.assessment  # Fetch the related assessment
        section = assessment.section  # Fetch the related section

        # Get the faculty and students group names
        faculty_group_name = f"faculty_section_{section.pk}"
        students_group_name = f"students_section_{section.pk}"

        # Get the groups
        faculty_group = Group.objects.get(name=faculty_group_name)
        students_group = Group.objects.get(name=students_group_name)

        # Assign permissions to the faculty group
        assign_perm('obesystem.view_question', faculty_group, instance)
        assign_perm('obesystem.change_question', faculty_group, instance)
        assign_perm('obesystem.delete_question', faculty_group, instance)

        # Assign view permissions to the students group
        assign_perm('obesystem.view_question', students_group, instance)

@receiver(post_delete, sender=Question)
def remove_question_permissions(sender, instance, **kwargs):
    """
    Remove object-level permissions when a question is deleted.
    """
    print('question remove signal')
    assessment = instance.assessment  # Fetch the related assessment
    section = assessment.section  # Fetch the related section

    # Get the faculty and students group names
    faculty_group_name = f"faculty_section_{section.pk}"
    students_group_name = f"students_section_{section.pk}"

    # Get the groups
    faculty_group = Group.objects.get(name=faculty_group_name)
    students_group = Group.objects.get(name=students_group_name)

    # Remove permissions from the faculty group
    remove_perm('obesystem.view_question', faculty_group, instance)
    remove_perm('obesystem.change_question', faculty_group, instance)
    remove_perm('obesystem.delete_question', faculty_group, instance)

    # Remove permissions from the students group
    remove_perm('obesystem.view_question', students_group, instance)