from django.db import models
from .section import Section
from django.core.validators import MinValueValidator

class Assessment(models.Model):
    title = models.CharField(max_length=100)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='assessments')
    date = models.DateField()
    marks = models.FloatField(validators=[MinValueValidator(0.0)], help_text="Enter the total marks for the assessment.")
    ASSESSMENT_TYPES = [
        ('quiz', 'Quiz'),
        ('assignment', 'Assignment'),
        ('midterm', 'Midterm'),
        ('final', 'Final Exam'),
    ]
    type = models.CharField(max_length=20, choices=ASSESSMENT_TYPES)

    def __str__(self):
        return f"{self.section.course.name} - {self.title} ({self.type})"
