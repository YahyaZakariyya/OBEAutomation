from django.db import models
from .course import Course
from .plo import ProgramLearningOutcome
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator


class CourseLearningOutcome(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='course_outcomes')
    CLO = models.IntegerField(
        choices=[(i, str(i)) for i in range(1, 16)],  # Dropdown from 1 to 15
        validators=[MinValueValidator(1)]
    )
    description = models.TextField()
    mapped_to_PLO = models.ManyToManyField(
        ProgramLearningOutcome, related_name='related_clos'
    )
    weightage = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="Weightage must be between 0 and 100."
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['course', 'CLO'], name='unique_clo_per_course')
        ]

    def save(self, *args, **kwargs):
        # First, save the object to generate an ID (if it's a new object)
        super().save(*args, **kwargs)
        
        # Now that the object is saved, we can safely access ManyToMany relationships
        for plo in self.mapped_to_PLO.all():
            total_weightage = sum(clo.weightage for clo in plo.related_clos.all())
            if total_weightage > 100:
                raise ValidationError(f"Total weightage for CLOs mapped to PLO {plo.PLO} cannot exceed 100%. Current total: {total_weightage}%.")

    def __str__(self):
        return f"CLO {self.CLO}: {self.description}"