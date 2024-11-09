from django.core.exceptions import ValidationError
from django.db import models

class AssessmentBreakdown(models.Model):
    section = models.OneToOneField('Section', on_delete=models.CASCADE)  # Ensures only one breakdown per section

    # Individual fields for each assessment type
    assignment_weightage = models.PositiveIntegerField(default=0)
    quiz_weightage = models.PositiveIntegerField(default=0)
    lab_weightage = models.PositiveIntegerField(default=0)
    mid_weightage = models.PositiveIntegerField(default=0)
    final_weightage = models.PositiveIntegerField(default=0)
    project_weightage = models.PositiveIntegerField(default=0)

    def clean(self):
        # Validate that the total weightage equals 100
        total_weightage = (
            self.assignment_weightage +
            self.quiz_weightage +
            self.lab_weightage +
            self.mid_weightage +
            self.final_weightage +
            self.project_weightage
        )
        if total_weightage != 100:
            raise ValidationError("The total weightage must be exactly 100%.")

    def save(self, *args, **kwargs):
        self.full_clean()  # Perform validation before saving
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Assessment Breakdown for {self.section}"

    class Meta:
        verbose_name = "Assessment Breakdown"
        verbose_name_plural = "Assessment Breakdowns"
