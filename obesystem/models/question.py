from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

class Question(models.Model):
    assessment = models.ForeignKey(
        "Assessment",
        on_delete=models.CASCADE,
        related_name='questions'
    )
    number = models.PositiveIntegerField()  # Auto-incremented question number
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
        return f"Q{self.number}"


@receiver(post_save, sender=Question)
def validate_clo_post_save(sender, instance, **kwargs):
    """Ensure at least one CLO is selected after saving the Question."""
    if not instance.clo.exists():
        raise ValidationError("At least one CLO must be mapped to this question.")
