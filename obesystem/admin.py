from django.contrib import admin
from django.urls import path, reverse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.utils.html import format_html
from django.core.exceptions import ValidationError
from django.contrib.auth.admin import UserAdmin
from .models import (CustomUser, Program, Course, Section, 
                     ProgramLearningOutcome, CourseLearningOutcome, 
                     Assessment, Question)

class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
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

# class SectionAdmin(admin.ModelAdmin):
#     list_display = ('course', 'semester', 'section', 'batch', 'year', 'faculty')
#     list_filter = ('semester', 'batch', 'year', 'faculty')
#     search_fields = ('course__name', 'faculty__username', 'faculty__first_name', 'faculty__last_name')
    
#     # To show the students field as a dual list box
#     filter_horizontal = ('students',)
    
#     fieldsets = (
#         (None, {
#             'fields': ('course', 'semester', 'section', 'batch', 'year', 'faculty')
#         }),
#         ('Enrolled Students', {
#             'fields': ('students',),
#         }),
#     )

#     def formfield_for_foreignkey(self, db_field, request, **kwargs):
#         if db_field.name == "faculty" and not request.user.is_superuser:
#             kwargs["queryset"] = CustomUser.objects.filter(role='faculty')
#         return super().formfield_for_foreignkey(db_field, request, **kwargs)

class SectionAdmin(admin.ModelAdmin):
    list_display = ('course', 'semester', 'section', 'batch', 'year', 'faculty')
    list_filter = ('semester', 'batch', 'year')
    search_fields = ('course__name', 'faculty__username', 'faculty__first_name', 'faculty__last_name')
    filter_horizontal = ('students',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.is_staff:
            return qs
        return qs.filter(faculty=request.user)

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]  # All fields read-only for everyone

    def has_add_permission(self, request):
        return request.user.is_superuser or request.user.is_staff  # Only allow superusers and admins to add sections

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.is_staff  # Only allow superusers and admins to edit sections

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.is_staff  # Only allow superusers and admins to delete sections

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:section_id>/assessments/', self.admin_site.admin_view(self.assessment_view), name='section_assessments'),
        ]
        return custom_urls + urls

    def assessment_view(self, request, section_id):
        section = Section.objects.get(pk=section_id)
        assessments = section.assessments.all()
        context = {
            'section': section,
            'assessments': assessments,
            'add_assessment_url': reverse('admin:your_app_assessment_add') + f'?section={section_id}',
            'opts': self.model._meta,
            'has_change_permission': self.has_change_permission(request, section),
        }
        return TemplateResponse(request, 'admin/section_assessment_view.html', context)

    def response_change(self, request, obj):
        if "_continue" in request.POST:
            return redirect('admin:section_assessments', section_id=obj.pk)
        return super().response_change(request, obj)
        
class ProgramLearningOutcomeAdmin(admin.ModelAdmin):
    def display_str(self, obj):
        return str(obj)
    display_str.short_description = 'PLO Details'
    list_display = ('program','display_str')
    list_filter = ('program',)
    search_fields = ('description',)

class CourseLearningOutcomeAdmin(admin.ModelAdmin):
    list_display = ('course', 'description')
    list_filter = ('course',)
    search_fields = ('description',)
    filter_horizontal = ('mapped_to_PLO',)

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 3

class AssessmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'section', 'date', 'type')
    list_filter = ('section', 'type')
    search_fields = ('title',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(section__faculty=request.user)

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser or (obj and obj.section.faculty == request.user):
            return []
        return [f.name for f in self.model._meta.fields]  # All fields read-only for non-superusers and non-assigned faculty

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser or (obj and obj.section.faculty == request.user):
            return True
        return False

    def has_add_permission(self, request):
        if request.user.is_superuser or request.user.role == 'faculty':
            return True
        return False

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser or (obj and obj.section.faculty == request.user):
            return True
        return False

    def has_module_permission(self, request):
        """Hide 'Assessments' from non-superuser users."""
        return request.user.is_superuser
    
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('assessment', 'text', 'marks', 'clo')
    list_filter = ('assessment',)
    search_fields = ('text',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(assessment__section__faculty=request.user)

    def has_module_permission(self, request):
        """Restrict direct visibility of Questions to superusers."""
        return request.user.is_superuser


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Program, ProgramAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(ProgramLearningOutcome, ProgramLearningOutcomeAdmin)
admin.site.register(CourseLearningOutcome, CourseLearningOutcomeAdmin)
admin.site.register(Assessment, AssessmentAdmin)
admin.site.register(Question, QuestionAdmin)