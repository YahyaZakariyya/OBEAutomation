from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from programs.models import Program

class Course(models.Model):
    course_id = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    credit_hours = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(4)
        ])
    programs = models.ManyToManyField(Program, related_name='courses')

    def __str__(self):
        return f"{self.name} ({self.course_id})"

    class Meta:
        unique_together = ('course_id', 'name', 'credit_hours')