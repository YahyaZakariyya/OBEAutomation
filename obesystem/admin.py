from django.contrib import admin
from django.core.exceptions import ValidationError
from django.contrib.auth.admin import UserAdmin
from .models import (CustomUser, Department, Program, Course, Section, 
                     ProgramLearningOutcome, CourseLearningOutcome, 
                     Assessment, Question, Enrollment)

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role', 'department',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('role', 'department',)}),
    )
    list_display = ['username', 'email', 'role', 'department', 'is_active']

class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class ProgramAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'hod')
    list_filter = ('department',)
    search_fields = ('name',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "hod" and not request.user.is_superuser:
            kwargs["queryset"] = CustomUser.objects.filter(role='head_of_department')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'program')
    list_filter = ('program',)
    search_fields = ('code', 'name')

class SectionAdmin(admin.ModelAdmin):
    list_display = ('course', 'faculty', 'semester')
    list_filter = ('semester', 'course')
    search_fields = ('course__name',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "faculty" and not request.user.is_superuser:
            kwargs["queryset"] = CustomUser.objects.filter(role='faculty')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class CLOInline(admin.TabularInline):
    model = CourseLearningOutcome
    extra = 3

class ProgramLearningOutcomeAdmin(admin.ModelAdmin):
    list_display = ('program', 'description')
    list_filter = ('program',)
    search_fields = ('description',)
    inlines = [CLOInline]

class CourseLearningOutcomeAdmin(admin.ModelAdmin):
    list_display = ('course', 'description')
    list_filter = ('course',)
    search_fields = ('description',)

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 3

class AssessmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'section', 'date', 'type')
    list_filter = ('section', 'type')
    search_fields = ('title',)
    inlines = [QuestionInline]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'section' and not request.user.is_superuser:
            kwargs['queryset'] = Section.objects.filter(faculty=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        field = super(AssessmentAdmin, self).formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name == 'weightage':
            field.help_text = "Max weightage: 2.5 for Quizzes/Assignments, 30 for Midterms, 50 for Finals."
        return field

    def save_model(self, request, obj, form, change):
        if obj.type == 'quiz' or obj.type == 'assignment':
            max_weightage = 2.5
        elif obj.type == 'midterm':
            max_weightage = 30
        elif obj.type == 'final':
            max_weightage = 50
        else:
            max_weightage = 1  # default case, though all types should be covered

        if obj.weightage > max_weightage:
            raise ValidationError(f"The maximum weightage for {obj.type} is {max_weightage}.")
        super().save_model(request, obj, form, change)

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('assessment', 'text', 'marks', 'clo')
    list_filter = ('assessment',)
    search_fields = ('text',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'assessment' and not request.user.is_superuser:
            kwargs['queryset'] = Assessment.objects.filter(section__faculty=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'section')
    search_fields = ('student__username', 'section__course__name')

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Program, ProgramAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(ProgramLearningOutcome, ProgramLearningOutcomeAdmin)
admin.site.register(CourseLearningOutcome, CourseLearningOutcomeAdmin)
admin.site.register(Assessment, AssessmentAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Enrollment, EnrollmentAdmin)