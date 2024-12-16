from django.db import models
from django.core.exceptions import ValidationError
from users.models import CustomUser
from .question import Question

class StudentQuestionScore(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    marks_obtained = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,  # Default value set to 0
    )

    class Meta:
        unique_together = ('student', 'question')

    def clean(self):
        # Access the total marks from the related Question model
        if self.marks_obtained > self.question.marks:
            raise ValidationError(
                f"Marks obtained ({self.marks_obtained}) cannot exceed total marks for the question ({self.question.marks})."
            )

    def save(self, *args, **kwargs):
        # Call clean() method to enforce validation before saving
        self.clean()
        super().save(*args, **kwargs)