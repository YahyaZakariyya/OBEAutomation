from django.contrib import admin
from django import forms
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
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

class SectionAdmin(admin.ModelAdmin):
    list_display = ('course', 'semester', 'section', 'batch', 'year', 'faculty')
    list_filter = ('semester', 'batch', 'year')
    search_fields = ('course__name', 'faculty__username', 'faculty__first_name', 'faculty__last_name')

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super().get_queryset(request)
        return super().get_queryset(request).filter(faculty=request.user)

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser or (obj is None or obj.faculty == request.user)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        section = get_object_or_404(Section, pk=object_id)
        extra_context = extra_context or {}
        extra_context['add_assessment_url'] = reverse('admin:%s_%s_add' % (
            Assessment._meta.app_label, Assessment._meta.model_name)) + f'?section={object_id}'
        extra_context['view_assessments_url'] = reverse('admin:%s_%s_changelist' % (
            Assessment._meta.app_label, Assessment._meta.model_name)) + f'?section__id__exact={object_id}'
        
        # Print to debug
        print("Extra context:", extra_context)

        return super(SectionAdmin, self).change_view(request, object_id, form_url, extra_context)


            
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

class AssessmentAdminForm(forms.ModelForm):
    class Meta:
        model = Assessment
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make section field read-only if section is already set
        if self.instance and self.instance.pk:
            self.fields['section'].disabled = True
        elif 'section' in self.initial:
            self.fields['section'].queryset = Section.objects.filter(pk=self.initial['section'])
            self.fields['section'].initial = Section.objects.get(pk=self.initial['section'])
            self.fields['section'].disabled = True

class AssessmentAdmin(admin.ModelAdmin):
    form = AssessmentAdminForm
    list_display = ('title', 'section', 'date', 'type')
    list_filter = ('section', 'type', 'date')
    search_fields = ('title',)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not request.user.is_superuser:
            form.base_fields['section'].queryset = Section.objects.filter(faculty=request.user)
        return form

    def add_view(self, request, form_url='', extra_context=None):
        section_id = request.GET.get('section')
        if section_id:
            extra_context = extra_context or {}
            extra_context['section'] = Section.objects.get(pk=section_id)
        return super().add_view(request, form_url, extra_context)

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser and not change:
            section_id = request.GET.get('section')
            if section_id:
                obj.section = Section.objects.get(pk=section_id)
            if obj.section.faculty != request.user:
                raise ValidationError("You cannot add assessments to a section that you do not teach.")
        super().save_model(request, obj, form, change)

    def response_add(self, request, obj, post_url_continue=None):
        return HttpResponseRedirect(f'/obesystem/section/{obj.section.id}/change/')

    def response_change(self, request, obj):
        return HttpResponseRedirect(f'/obesystem/section/{obj.section.id}/change/')
    
    def has_module_permission(self, request):
        # Hide 'Assessments' from faculty users
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