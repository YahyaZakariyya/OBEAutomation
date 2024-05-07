from django.db import models

# old
# class Program(models.Model):
#     program_code = models.CharField(max_length=255, unique=True) # Dynamic character type
#     program_name = models.CharField(max_length=255, unique=True) # Dynamic character type

#     def __str__(self):
#         return self.program_name

class Director(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class HeadOfDepartment(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} - {self.department}"

class Faculty(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)

    def __str__(self):
        return self.name



class Program(models.Model):
    name = models.CharField(max_length=100)
    director = models.ForeignKey('Director', on_delete=models.SET_NULL, null=True)
    hod = models.ForeignKey('HeadOfDepartment', on_delete=models.SET_NULL, null=True)
    
    def __str__(self):
        return self.name


class ProgramLearningOutcome(models.Model):
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='outcomes')
    description = models.TextField()

    def __str__(self):
        return f"{self.program.name} - {self.description[:50]}"

class Course(models.Model):
    code = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=100)
    credit_hrs = models.IntegerField()
    program = models.ForeignKey(Program, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


# class CourseLearningOutcome(models.Model):
#     course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='learning_outcomes')
#     description = models.TextField()
    
#     def __str__(self):
#         return f"{self.course.name} - {self.description[:50]}"

# class CLO(models.Model):
#     plo = models.ForeignKey(PLO, on_delete=models.CASCADE)
#     course = models.ForeignKey(Course, on_delete=models.CASCADE)
#     CLO_details = models.TextField() # Dynamic character field

class CourseLearningOutcome(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='learning_outcomes')
    plos = models.ManyToManyField('ProgramLearningOutcome', related_name='clos')
    description = models.TextField()

    def __str__(self):
        return f"{self.course.name} - {self.description[:50]}"


class Section(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='sections')
    faculty = models.ForeignKey('Faculty', on_delete=models.SET_NULL, null=True)
    section_name = models.CharField(max_length=20)
    
    def __str__(self):
        return f"{self.course.name} - {self.section_name}"


class Assessment(models.Model):
    title = models.CharField(max_length=100)
    # section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='assessments')
    course = models.ForeignKey('Course', on_delete=models.CASCADE)
    # assessment_number = models.IntegerField()
    assessment_date = models.DateField()
    # assessment_weightage = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    assessment_marks = models.FloatField()
    ASSESSMENT_TYPES = [
        ('Quiz', 'Quiz'),
        ('Assignment', 'Assignment'),
        ('Mids', 'Midterms'),
        ('Finals', 'Finals'),
    ]
    assessment_type = models.CharField(max_length=20, choices=ASSESSMENT_TYPES)

    def __str__(self):
        return self.title
    

class Question(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    clo = models.ForeignKey('CourseLearningOutcome', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.text[:50]}"
