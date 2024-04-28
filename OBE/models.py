from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Program(models.Model):
    program_code = models.CharField(max_length=255, unique=True) # Dynamic character type
    program_name = models.CharField(max_length=255, unique=True) # Dynamic character type

    def __str__(self):
        return self.program_name

class PLO(models.Model):
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    PLO_details = models.TextField() # Dynamic character field

class Course(models.Model):
    course_code = models.CharField(max_length=255, unique=True)
    course_name = models.CharField(max_length=255, unique=True)
    credit_hrs = models.IntegerField()
    program = models.ForeignKey(Program, on_delete=models.CASCADE)

    def __str__(self):
        return self.course_name

class CLO(models.Model):
    plo = models.ForeignKey(PLO, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    CLO_details = models.TextField() # Dynamic character field

class Assessment(models.Model):
    course = models.ForeignKey('Course', on_delete=models.CASCADE)
    assessment_number = models.IntegerField()
    assessment_date = models.DateField()
    assessment_weightage = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    assessment_marks = models.FloatField()
    ASSESSMENT_TYPES = [
        ('Quiz', 'Quiz'),
        ('Assignment', 'Assignment'),
        ('Mids', 'Midterms'),
        ('Finals', 'Finals'),
    ]
    assessment_type = models.CharField(max_length=20, choices=ASSESSMENT_TYPES)

    def __str__(self):
        return str(self.assessment_type) + " " + str(self.assessment_number)