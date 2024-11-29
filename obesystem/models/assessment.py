from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from .assessment_breakdown import AssessmentBreakdown

class Assessment(models.Model):
    title = models.CharField(max_length=100)
    section = models.ForeignKey('Section', on_delete=models.CASCADE, related_name='assessments')
    date = models.DateField()
    ASSESSMENT_TYPES = [
        ('quiz', 'Quiz'),
        ('assignment', 'Assignment'),
        ('midterm', 'Midterm'),
        ('final', 'Final Exam'),
        ('lab', 'Lab'),
        ('project', 'Project'),
    ]
    type = models.CharField(max_length=20, choices=ASSESSMENT_TYPES)
    weightage = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
    )

    def clean(self):
        # Validate against AssessmentBreakdown
        assessment_breakdown = AssessmentBreakdown.objects.filter(section=self.section).first()
        if not assessment_breakdown:
            raise ValidationError(f"No Assessment Breakdown found for section {self.section}.")

        # Map assessment type to the weightage field in AssessmentBreakdown
        weightage_mapping = {
            'quiz': assessment_breakdown.quiz_weightage,
            'assignment': assessment_breakdown.assignment_weightage,
            'midterm': assessment_breakdown.mid_weightage,
            'final': assessment_breakdown.final_weightage,
            'lab': assessment_breakdown.lab_weightage,
            'project': assessment_breakdown.project_weightage,
        }

        # Validate total weightage of assessments of the same type
        overall_weightage = weightage_mapping.get(self.type)
        if overall_weightage is None or overall_weightage <= 0:
            raise ValidationError(f"Invalid or zero weightage configured for assessment type '{self.type}'.")

        # Validate that the total weightage for this assessment type sums to 100%
        existing_assessments = Assessment.objects.filter(
            section=self.section,
            type=self.type
        ).exclude(pk=self.pk)

        total_type_weightage = sum(a.weightage for a in existing_assessments) + self.weightage
        if total_type_weightage > 100:
            raise ValidationError(
                f"Total weightage for assessments of type '{self.type}' exceeds 100%. "
                f"Current total: {total_type_weightage}%. Please adjust weightages."
            )

    def get_total_marks(self):
        """
        Calculate total marks for the assessment based on associated questions.
        """
        return sum(question.marks for question in self.questions.all())

    def save(self, *args, **kwargs):
        self.full_clean()  # Validate before saving
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.section.course.name} - {self.title} ({self.type})"
    
    class Meta:
        permissions = [
            ('can_add_question', 'Can add question to this assessment'),
        ]