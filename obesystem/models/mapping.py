from django.db import models
from .program import Program
from .plo import ProgramLearningOutcome
from .clo import CourseLearningOutcome
from django.core.exceptions import ValidationError

class ProgramCLOMapping(models.Model):
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name="clo_mappings")
    plo = models.ForeignKey(ProgramLearningOutcome, on_delete=models.CASCADE, related_name="clo_mappings")
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name="program_clo_mappings")
    clo = models.ForeignKey(CourseLearningOutcome, on_delete=models.CASCADE, related_name="program_mappings")
    weightage = models.FloatField()

    class Meta:
        unique_together = ('program', 'course', 'clo', 'plo')

    def __str__(self):
        return f"{self.program} - {self.course} - {self.clo} to {self.plo} (Weightage: {self.weightage}%)"

    def clean(self):
        """Ensures that the total weightage for CLO mappings for this course in this program does not exceed 100% 
           and automatically distributes weightage if a CLO maps to multiple PLOs."""
        
        # Get all mappings for this CLO within the same program and course
        mappings = ProgramCLOMapping.objects.filter(program=self.program, course=self.course, clo=self.clo).exclude(pk=self.pk)
        
        # Count existing mappings plus this instance
        num_plos = mappings.count() + 1

        # Automatically distribute weightage if mapping to multiple PLOs
        if num_plos > 1:
            # Calculate the evenly distributed weightage
            suggested_weightage = 100.0 / num_plos

            # Set weightage for the current instance
            self.weightage = suggested_weightage

            # Validate that all mappings have distributed weightage
            for mapping in mappings:
                if mapping.weightage != suggested_weightage:
                    raise ValidationError(f"Each CLO mapped to multiple PLOs should have a distributed weightage of {suggested_weightage}%.")
        
        # Ensure total weightage for the program-course combination does not exceed 100%
        total_weightage = sum(mapping.weightage for mapping in mappings) + self.weightage
        if total_weightage > 100:
            raise ValidationError("Total weightage for all CLO mappings in this course and program must not exceed 100%.")

    # def save(self, *args, **kwargs):
    #     # Automatically calculate and assign distributed weightage if mapping to multiple PLOs
    #     mappings = ProgramCLOMapping.objects.filter(program=self.program, clo=self.clo)
    #     num_plos = mappings.count() + 1  # including the current instance

    #     # Set the weightage for each mapping to evenly distribute 100% across all mappings
    #     distributed_weightage = 100.0 / num_plos

    #     # Assign the calculated weightage to the current mapping
    #     self.weightage = distributed_weightage

    #     # Update existing mappings with the new distributed weightage
    #     super().save(*args, **kwargs)
    #     mappings.update(weightage=distributed_weightage)

    def save(self, *args, **kwargs):
        # Call clean to ensure validations are checked before saving
        self.clean()
        super().save(*args, **kwargs)
