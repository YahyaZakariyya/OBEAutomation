from django.db import models
from users.models import CustomUser

class FacultyCourse(models.Model):
    faculty = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE)  # Use string reference

    class Meta:
        unique_together = ('faculty', 'course')

    def __str__(self):
        return f"{self.faculty.username} - {self.course.name}"
