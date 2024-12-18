from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Program
from courses.models import Course

@receiver(post_delete, sender=Program)
def delete_related_courses(sender, instance, **kwargs):
    """
    Deletes all courses associated with the program when the program is deleted.
    """
    for course in instance.course_set.all():
        course.delete()