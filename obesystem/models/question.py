from django.db import models
from django.core.validators import MinValueValidator

class Question(models.Model):
    assessment = models.ForeignKey(
        "Assessment",
        on_delete=models.CASCADE,
        related_name='questions'
    )
    marks = models.FloatField(
        validators=[MinValueValidator(0.1)],
        help_text="Marks must be a positive number."
    )
    clo = models.ManyToManyField(
        "CourseLearningOutcome",
        related_name='questions',
        blank=False,
        help_text="At least one CLO must be mapped to this question."
    )

    def __str__(self):
        return f"Q"