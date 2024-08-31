from django.contrib import admin
from django.core.exceptions import ValidationError
from django.contrib.auth.admin import UserAdmin
from .models import (CustomUser, Program, Course, Section, 
                     ProgramLearningOutcome, CourseLearningOutcome, 
                     Assessment, Question)

class CustomUserAdmin(UserAdmin):
    # Define the fields to be displayed in the admin panel
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    # Override the add_fieldsets to remove 'role' from creation form if necessary
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'role'),
        }),
    )

    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)

class ProgramAdmin(admin.ModelAdmin):
    list_display = ('name', 'hod')
    search_fields = ('name',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "hod" and not request.user.is_superuser:
            kwargs["queryset"] = CustomUser.objects.filter(role='head_of_department')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class CourseAdmin(admin.ModelAdmin):
    list_display = ('course_id', 'name', 'program')
    list_filter = ('program',)
    search_fields = ('course_id', 'name')

class SectionAdmin(admin.ModelAdmin):
    list_display = ('course', 'semester', 'section', 'batch', 'year', 'faculty')
    list_filter = ('semester', 'batch', 'year', 'faculty')
    search_fields = ('course__name', 'faculty__username', 'faculty__first_name', 'faculty__last_name')
    
    # To show the students field as a dual list box
    filter_horizontal = ('students',)
    
    fieldsets = (
        (None, {
            'fields': ('course', 'semester', 'section', 'batch', 'year', 'faculty')
        }),
        ('Enrolled Students', {
            'fields': ('students',),
        }),
    )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "faculty" and not request.user.is_superuser:
            kwargs["queryset"] = CustomUser.objects.filter(role='faculty')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

# class SectionAdmin(admin.ModelAdmin):
#     list_display = ('course', 'faculty', 'semester')
#     list_filter = ('semester', 'course')
#     search_fields = ('course__name',)

#     def formfield_for_foreignkey(self, db_field, request, **kwargs):
#         if db_field.name == "faculty" and not request.user.is_superuser:
#             kwargs["queryset"] = CustomUser.objects.filter(role='faculty')
#         return super().formfield_for_foreignkey(db_field, request, **kwargs)

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


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Program, ProgramAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(ProgramLearningOutcome, ProgramLearningOutcomeAdmin)
admin.site.register(CourseLearningOutcome, CourseLearningOutcomeAdmin)
admin.site.register(Assessment, AssessmentAdmin)
admin.site.register(Question, QuestionAdmin)