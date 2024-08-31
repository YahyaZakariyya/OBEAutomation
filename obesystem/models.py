from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

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
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    credit_hours = models.IntegerField()
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='courses')

    def __str__(self):
        return f"{self.code} - {self.name}"

class Section(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='sections')
    faculty = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='taught_sections')
    semester = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.course.name} - {self.semester}"

class ProgramLearningOutcome(models.Model):
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='program_outcomes')
    name = models.CharField(max_length=100, default='Unnamed PLO')
    description = models.TextField()

    def __str__(self):
        return f"{self.program.name} - PLO"

class CourseLearningOutcome(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='course_outcomes')
    name = models.CharField(max_length=100, default='Unnamed CLO')
    description = models.TextField()
    related_plo = models.ForeignKey(ProgramLearningOutcome, on_delete=models.CASCADE, related_name='related_clos')

    def __str__(self):
        return f"{self.course.name} - CLO"

class Assessment(models.Model):
    title = models.CharField(max_length=100)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='assessments')
    date = models.DateField()
    weightage = models.FloatField(default=0, help_text="Max weightage varies by assessment type.")

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
    marks = models.IntegerField()
    weightage = models.FloatField(default=0, help_text="Maximum weightage is 10.")
    clo = models.ForeignKey(CourseLearningOutcome, on_delete=models.CASCADE, related_name='questions')

    def __str__(self):
        return f"{self.text[:50]} - {self.marks} Marks"

class Enrollment(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='enrollments')
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='enrolled_students')

    def __str__(self):
        return f"{self.student.username} enrolled in {self.section.course.name} - {self.section.semester}"


class Report(models.Model):
    pass