from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.validators import MinValueValidator, MaxValueValidator
import datetime

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('faculty', 'Faculty Member'),
        ('student', 'Student'),
    )
    role = models.CharField(choices=ROLE_CHOICES, max_length=20, default='student')

    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A group is a collection of permissions.',
        related_name="customuser_set",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="customuser_set",
        related_query_name="user",
    )

    def __str__(self):
        return f"{self.username} ({self.role})"

class Program(models.Model):
    name = models.CharField(max_length=100)
    hod = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='program_heads', limit_choices_to={'role': 'faculty'})

    def __str__(self):
        return self.name

class Course(models.Model):
    course_id = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    credit_hours = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(4)
        ])
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='courses')

    def __str__(self):
        return f"{self.name} - {self.course_id}"

class Section(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='sections')
    faculty = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='taught_sections',
        limit_choices_to={'role': 'faculty'}  # Restrict to faculty members
    )
    
    # Updated 'semester' field
    SEMESTER_CHOICES = [(str(i), str(i)) for i in range(1, 11)]  # Choices from '1' to '10'
    semester = models.CharField(
        max_length=2,
        choices=SEMESTER_CHOICES,
        default='1'
    )
    
    # New 'section' field with A-Z choices
    SECTION_CHOICES = [(chr(i), chr(i)) for i in range(65, 91)]  # 'A' to 'Z'
    section = models.CharField(
        max_length=1,
        choices=SECTION_CHOICES,
        default='A'
    )
    
    # New 'batch' field with specific options
    BATCH_CHOICES = (
        ('Spring', 'Spring'),
        ('Summer', 'Summer'),
        ('Fall', 'Fall'),
    )
    batch = models.CharField(
        max_length=6,
        choices=BATCH_CHOICES,
        null=False,
        blank=False
    )
    
    # New 'year' field with dynamic year choices
    CURRENT_YEAR = datetime.datetime.now().year
    YEAR_CHOICES = [(str(year), str(year)) for year in range(CURRENT_YEAR, CURRENT_YEAR + 10)]  # Next 10 years
    year = models.CharField(
        max_length=4,
        choices=YEAR_CHOICES
    )
    
    # New 'students' field to enroll multiple students
    students = models.ManyToManyField(
        CustomUser,
        related_name='enrolled_sections',
        limit_choices_to={'role': 'student'},
        blank=True
    )

    def __str__(self):
        return f"{self.course.name} - {self.semester}"

class ProgramLearningOutcome(models.Model):
    PLO_CHOICES = [(i, str(i)) for i in range(1, 16)]

    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='program_outcomes')
    PLO = models.PositiveIntegerField(
        choices=PLO_CHOICES,
        validators=[MinValueValidator(1)],
    )
    heading = models.CharField(max_length=255)
    description = models.TextField()
    weightage = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="PLO weightage must be between 0 and 100."
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['program', 'PLO'], name='unique_plo_per_program')
        ]

    def clean(self):
        # Validate that the total weightage for all PLOs in a program does not exceed 100%
        total_weightage = sum(plo.weightage for plo in ProgramLearningOutcome.objects.filter(program=self.program).exclude(id=self.id))
        total_weightage += self.weightage  # Add current PLO weightage

        if total_weightage > 100:
            raise ValidationError(f"The total weightage for PLOs in the program {self.program.name} cannot exceed 100%. Current total: {total_weightage}%.")

    def __str__(self):
        return f"PLO {self.PLO}: {self.heading}:"
    
class CourseLearningOutcome(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='course_outcomes')
    CLO = models.IntegerField(
        choices=[(i, str(i)) for i in range(1, 16)],  # Dropdown from 1 to 15
        validators=[MinValueValidator(1)]
    )
    description = models.TextField()
    mapped_to_PLO = models.ManyToManyField(
        ProgramLearningOutcome, related_name='related_clos'
    )
    weightage = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="Weightage must be between 0 and 100."
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['course', 'CLO'], name='unique_clo_per_course')
        ]

    def save(self, *args, **kwargs):
        # First, save the object to generate an ID (if it's a new object)
        super().save(*args, **kwargs)
        
        # Now that the object is saved, we can safely access ManyToMany relationships
        for plo in self.mapped_to_PLO.all():
            total_weightage = sum(clo.weightage for clo in plo.related_clos.all())
            if total_weightage > 100:
                raise ValidationError(f"Total weightage for CLOs mapped to PLO {plo.PLO} cannot exceed 100%. Current total: {total_weightage}%.")

    def __str__(self):
        return f"CLO {self.CLO}: {self.description}"

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