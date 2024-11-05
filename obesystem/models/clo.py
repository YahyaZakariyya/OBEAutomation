from django.db import models
from .course import Course
from django.core.validators import MinValueValidator

class CourseLearningOutcome(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='course_outcomes')
    CLO = models.IntegerField(
        choices=[(i, str(i)) for i in range(1, 16)],  # Dropdown from 1 to 15
        validators=[MinValueValidator(1)]
    )
    heading = models.CharField(max_length=255)
    description = models.TextField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['course', 'CLO'], name='unique_clo_per_course')
        ]

    def __str__(self):
        return f"CLO {self.CLO}: {self.heading}"