from django.db import models
from django.core.exceptions import ValidationError
from programs.models import Program
from courses.models import Course
from .clo import CourseLearningOutcome
from .plo import ProgramLearningOutcome

class PloCloMapping(models.Model):
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name="clo_mappings")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="program_clo_mappings")
    plo = models.ForeignKey(ProgramLearningOutcome, on_delete=models.CASCADE, related_name="clo_mappings")
    clo = models.ForeignKey(CourseLearningOutcome, on_delete=models.CASCADE, related_name="program_mappings")
    weightage = models.FloatField()  # Weightage for CLO in the context of its PLO (0-100)

    class Meta:
        unique_together = ('program', 'course', 'clo')  # Ensures one CLO maps to only one PLO per course

    def __str__(self):
        return f"{self.program} - {self.course} - {self.clo} maps to {self.plo} (Weightage: {self.weightage}%)"

    def clean(self):
        """
        Validates constraints:
        1. Each CLO maps to only one PLO.
        2. Total weightage of CLOs mapping to the same PLO within the same course must not exceed 100%.
        """

        # Ensure each CLO maps to only one PLO
        existing_mapping = PloCloMapping.objects.filter(course=self.course, clo=self.clo).exclude(pk=self.pk)
        if existing_mapping.exists():
            raise ValidationError(f"CLO '{self.clo}' is already mapped to another PLO in this course.")

        # Get all existing mappings for the same PLO and course (excluding this instance)
        mappings_for_same_plo = PloCloMapping.objects.filter(course=self.course, plo=self.plo).exclude(pk=self.pk)

        # Calculate the total weightage for this PLO
        total_weightage = sum(mapping.weightage for mapping in mappings_for_same_plo) + self.weightage

        # Ensure the total weightage for this specific PLO does not exceed 100%
        if total_weightage > 100:
            raise ValidationError(
                f"Total weightage for PLO '{self.plo}' in course '{self.course}' exceeds 100%. "
                f"Current total: {total_weightage}%."
            )

    def save(self, *args, **kwargs):
        # Validate before saving
        self.full_clean()
        super().save(*args, **kwargs)
