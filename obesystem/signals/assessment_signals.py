from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from guardian.shortcuts import assign_perm
from obesystem.models import Assessment
from django.contrib.auth.models import Permission

@receiver(post_save, sender=Assessment)
def assign_permissions_for_assessment(sender, instance, created, **kwargs):
    """
    Assign permissions to the faculty and students for the Assessment when it's created.
    """
    if created and instance.section:
        faculty_user = instance.section.faculty
        # Assign view, change, and delete permissions to the faculty
        if faculty_user:
            assign_perm('obesystem.view_assessment', faculty_user, instance)
            assign_perm('obesystem.change_assessment', faculty_user, instance)
            assign_perm('obesystem.delete_assessment', faculty_user, instance)

        # Assign view permissions to all students in the section
        students = instance.section.students.all()  # Assuming you have a related_name "students" in the Section model
        for student in students:
            assign_perm('obesystem.view_assessment', student, instance)


@receiver(post_delete, sender=Assessment)
def remove_permissions_for_assessment(sender, instance, **kwargs):
    """
    Remove permissions for the Assessment when it's deleted.
    """
    if instance.section:
        faculty_user = instance.section.faculty
        # Remove faculty permissions
        if faculty_user:
            permissions = Permission.objects.filter(
                codename__in=[
                    'view_assessment',
                    'change_assessment',
                    'delete_assessment',
                ]
            )
            faculty_user.user_permissions.remove(*permissions)

        # Remove view permissions for all students in the section
        students = instance.section.students.all()
        for student in students:
            permission = Permission.objects.get(codename='view_assessment')
            student.user_permissions.remove(permission)
