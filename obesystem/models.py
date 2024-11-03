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
    course_id = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    credit_hours = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(4)
        ])
    programs = models.ManyToManyField('Program', related_name='courses')

    def __str__(self):
        return f"{self.name} - {self.course_id}"

    class Meta:
        unique_together = ('course_id', 'name', 'credit_hours')

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

    def clean(self):
        # Ensure that the selected program is associated with the selected course
        if self.course and self.program:
            if self.program not in self.course.programs.all():
                raise ValidationError("Selected program is not associated with the chosen course.")

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