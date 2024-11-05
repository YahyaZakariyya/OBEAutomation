from django.db import models
from .assessment import Assessment
from .clo import CourseLearningOutcome
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

class Question(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    marks = models.IntegerField(validators=[MinValueValidator(1)], help_text="Marks must be a positive integer.")
    clo = models.ManyToManyField(CourseLearningOutcome, related_name='questions')

    def save(self, *args, **kwargs):
        # Save the Question instance to get an ID before assigning CLOs
        super(Question, self).save(*args, **kwargs)

        # If CLOs are present in kwargs, assign them
        if 'clo' in kwargs:
            self.clo.set(kwargs['clo'])  # Assign the CLOs after the Question has been saved

    def clean(self):
        # Validate marks do not exceed available marks in the assessment
        total_marks = sum(q.marks for q in self.assessment.questions.exclude(id=self.id))  # Sum marks of all other questions
        available_marks = self.assessment.marks - total_marks

        if self.marks > available_marks:
            raise ValidationError(f"Total marks for questions cannot exceed the assessment's marks. Available marks: {available_marks}.")
    
    def __str__(self):
        return f"{self.text[:50]} - {self.marks} Marks"