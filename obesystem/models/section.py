from django.db import models
from .course import Course
from .program import Program
from .custom_user import CustomUser
from django.core.exceptions import ValidationError
import datetime


class Section(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='sections')
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='sections', null=True, blank=True)
    
    faculty = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='taught_sections',
        limit_choices_to={'role': 'faculty'}
    )
    
    SEMESTER_CHOICES = [(str(i), str(i)) for i in range(1, 11)]
    semester = models.CharField(max_length=2, choices=SEMESTER_CHOICES, default='1')
    
    SECTION_CHOICES = [(chr(i), chr(i)) for i in range(65, 91)]
    section = models.CharField(max_length=1, choices=SECTION_CHOICES, default='A')
    
    BATCH_CHOICES = (
        ('Spring', 'Spring'),
        ('Summer', 'Summer'),
        ('Fall', 'Fall'),
    )
    batch = models.CharField(max_length=6, choices=BATCH_CHOICES)
    
    CURRENT_YEAR = datetime.datetime.now().year
    YEAR_CHOICES = [(str(year), str(year)) for year in range(CURRENT_YEAR, CURRENT_YEAR + 10)]
    year = models.CharField(max_length=4, choices=YEAR_CHOICES)
    
    students = models.ManyToManyField(
        CustomUser,
        related_name='enrolled_sections',
        limit_choices_to={'role': 'student'},
        blank=True
    )

    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('complete', 'Complete'),
    ]
    status = models.CharField(
        max_length=12,
        choices=STATUS_CHOICES,
        default='in_progress'
    )

    def __str__(self):
        return f"{self.course.name} - {self.semester}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['course', 'program', 'semester', 'section', 'batch', 'year'],
                name='unique_section_constraint'
            )
        ]
        permissions = [
            ('can_add_assessment', 'Can add assessment to this section'),
        ]

    def clean(self):
        # Ensure that the selected program is associated with the selected course
        if self.course and self.program:
            if self.program not in self.course.programs.all():
                raise ValidationError("Selected program is not associated with the chosen course.")