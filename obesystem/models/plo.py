from django.db import models
from django.core.exceptions import ValidationError
from .program import Program
from django.core.validators import MinValueValidator, MaxValueValidator

class ProgramLearningOutcome(models.Model):
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='program_outcomes')
    PLO = models.PositiveIntegerField(
        choices=[(i, str(i)) for i in range(1, 16)],
        validators=[MinValueValidator(1)],
    )
    heading = models.CharField(max_length=255)
    description = models.TextField()
    weightage = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="PLO weightage must be between 0.0 and 100.0"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['program', 'PLO'], name='unique_plo_per_program')
        ]

    def clean(self):
        # Validate that the total weightage for all PLOs in a program does not exceed 100%
        total_weightage = sum(plo.weightage for plo in ProgramLearningOutcome.objects.filter(program=self.program).exclude(id=self.id))

        if total_weightage+self.weightage > 100:
            raise ValidationError(f"The total weightage for PLOs in the program {self.program.name} cannot exceed 100%. Current total: {total_weightage}%. Remaining: {total_weightage%100}%")

    def __str__(self):
        return f"PLO {self.PLO}: {self.heading}:"