from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator

class CourseLearningOutcome(models.Model):
    course = models.ForeignKey("Course", on_delete=models.CASCADE, related_name='course_outcomes')
    CLO = models.IntegerField(
        choices=[(i, str(i)) for i in range(1, 16)],  # Dropdown from 1 to 15
        validators=[MinValueValidator(1)]
    )
    heading = models.CharField(max_length=255)
    description = models.TextField()
    weightage = models.FloatField(
        validators=[MinValueValidator(1), MaxValueValidator(100)],  # Ensure weightage is between 0 and 100
        default=1
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['course', 'CLO'], name='unique_clo_per_course')
        ]

    def __str__(self):
        return f"CLO {self.CLO}: {self.heading}"

    def clean(self):
        """
        Ensures that the total weightage of all CLOs in the same course does not exceed 100%.
        """
        super().clean()

        # Calculate total weightage for this course, excluding the current instance
        total_weightage = (
            CourseLearningOutcome.objects.filter(course=self.course)
            .exclude(pk=self.pk)  # Exclude the current instance to allow updates
            .aggregate(total=models.Sum('weightage'))['total'] or 0
        )

        # Add the current weightage to the total
        total_weightage += self.weightage

        # Check if total exceeds 100
        if total_weightage > 100:
            raise ValidationError(
                f"The total weightage of all CLOs for the course '{self.course}' exceeds 100%. "
                f"Current total: {total_weightage}%."
            )

    def save(self, *args, **kwargs):
        # Validate before saving
        self.full_clean()
        super().save(*args, **kwargs)
