from django.contrib import admin
from django import forms
from django.forms import BaseInlineFormSet, ValidationError
from django.urls import reverse
from django.utils.html import format_html
from django.shortcuts import get_object_or_404
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
    list_display = ('username', 'email', 'first_name', 'last_name', 'role')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    list_filter = ('role',)
    # ordering = ('username',)

class ProgramAdmin(admin.ModelAdmin):
    list_display = ('custom_program_name', 'custom_hod_name', 'view_courses', 'view_plos')
    search_fields = ('name',)

    def custom_program_name(self, obj):
        return obj.name
    custom_program_name.short_description = "Programs"
    custom_program_name.admin_order_field = "name"

    def custom_hod_name(self, obj):
        return obj.hod
    custom_hod_name.short_description = "Head of Department"
    custom_hod_name.admin_order_field = "hod"

    def view_courses(self, obj):
        url = f"/obesystem/course/?program__id={obj.id}"
        return format_html('<a class="btn btn-primary" href="{}">View Courses</a>', url)
    
    view_courses.short_description = "View Courses"
    view_courses.allow_tags = True  # Ensures the HTML is rendered correctly

    def view_plos(self, obj):
        url = f"/obesystem/programlearningoutcome/?program__id__exact={obj.id}"
        return format_html('<a class="btn btn-primary" href="{}">View PLOs</a>', url)
    
    view_plos.short_description = "View PLOs"
    view_plos.allow_tags = True  # Ensures the HTML is rendered correctly

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "hod" and not request.user.is_superuser:
            kwargs["queryset"] = CustomUser.objects.filter(role='head_of_department')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class CourseAdmin(admin.ModelAdmin):
    list_display = ('custom_course_name','credit_hours','view_clos')
    search_fields = ('name',)

    def custom_course_name(self, obj):
        return obj.name
    custom_course_name.short_description = "Course Title"
    custom_course_name.admin_order_field = "name"

    def view_clos(self, obj):
        url = f"/obesystem/courselearningoutcome/?course__id__exact={obj.id}"
        return format_html('<a class="btn btn-primary" href="{}">View CLOs</a>', url)
    view_clos.short_description = "View CLOs"
    view_clos.allow_tags = True  # Ensures the HTML is rendered correctly

class SectionAdmin(admin.ModelAdmin):
    list_display = ('course', 'semester', 'section', 'batch', 'year', 'faculty', 'view_assessments_button', 'create_assessment_button')
    list_filter = ('semester', 'batch', 'year')
    search_fields = ('course__name', 'faculty__username', 'faculty__first_name', 'faculty__last_name')

    # Method to add the "View Assessments" button
    def view_assessments_button(self, obj):
        # Direct URL for viewing assessments filtered by section ID
        url = f"/obesystem/assessment/?section__id__exact={obj.id}"
        return format_html('<a class="btn btn-primary" href="{}">View Assessments</a>', url)
    
    # Method to add the "Create Assessment" button
    def create_assessment_button(self, obj):
        # Direct URL for adding an assessment with the section pre-filled
        url = f"/obesystem/assessment/add/?section={obj.id}"
        return format_html('<a class="btn btn-primary" href="{}">Create Assessment</a>', url)

    create_assessment_button.short_description = 'Create Assessment'
    create_assessment_button.allow_tags = True

    view_assessments_button.short_description = 'View Assessments'
    view_assessments_button.allow_tags = True
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
        

        return super(SectionAdmin, self).change_view(request, object_id, form_url, extra_context)
            
class ProgramLearningOutcomeAdmin(admin.ModelAdmin):
    def display_str(self, obj):
        return str(obj)
    display_str.short_description = 'PLO Details'
    list_display = ('program','display_str')
    list_filter = ('program',)
    search_fields = ('description',)

    def has_module_permission(self, request):
        # Hide the course from the admin index page and sidebar
        return False

class CourseLearningOutcomeAdmin(admin.ModelAdmin):
    list_display = ('course', 'description')
    list_filter = ('course',)
    search_fields = ('description',)
    filter_horizontal = ('mapped_to_PLO',)

    def has_module_permission(self, request):
        # Hide the course from the admin index page and sidebar
        return False

# Custom inline formset to enforce the total marks constraint
class QuestionInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        total_marks = 0
        for form in self.forms:
            if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                total_marks += form.cleaned_data['marks']

        # Check if total marks exceed the assessment's total marks
        if total_marks > self.instance.marks:
            raise ValidationError(f"Total marks for questions ({total_marks}) exceed the available assessment marks ({self.instance.marks}).")

class QuestionInline(admin.TabularInline):
    model = Question
    formset = QuestionInlineFormSet
    extra = 1
    fields = ['text', 'marks', 'clo']

    def save_model(self, request, obj, form, change):
        # Save the object first to get the ID
        super().save_model(request, obj, form, change)
        # Handle Many-to-Many fields after the object has an ID
        form.save_m2m()

    # Prevent questions from being added until the assessment is created
    def has_add_permission(self, request, obj):
        if obj is None:
            return False  # No adding questions before an assessment is created
        return super().has_add_permission(request, obj)
    
class AssessmentForm(forms.ModelForm):
    class Meta:
        model = Assessment
        fields = ['title', 'section', 'date', 'marks', 'type']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(AssessmentForm, self).__init__(*args, **kwargs)

        if self.user is not None:
            # Superuser can see all sections
            if self.user.is_superuser:
                self.fields['section'].queryset = Section.objects.all()
            else:
                # Regular faculty member can only see their sections
                self.fields['section'].queryset = Section.objects.filter(faculty=self.user)

        if 'section' in self.initial:
            self.fields['section'].widget.attrs['readonly'] = True
            self.fields['section'].widget.attrs['disabled'] = 'disabled'

class AssessmentAdmin(admin.ModelAdmin):
    form = AssessmentForm
    inlines = [QuestionInline]

    def get_form(self, request, obj=None, **kwargs):
        form_class = super().get_form(request, obj, **kwargs)
        # Passing the user through kwargs
        class FormWithUser(form_class):
            def __init__(self, *args, **kwargs):
                kwargs['user'] = request.user
                super(FormWithUser, self).__init__(*args, **kwargs)

        return FormWithUser
    
    def get_inline_instances(self, request, obj=None):
        # Only show the inlines if the assessment has been created
        if obj is None:
            return []  # Don't show the inline questions during assessment creation
        return super().get_inline_instances(request, obj)

    def get_queryset(self, request):
        # Superuser can see all assessments
        if request.user.is_superuser:
            return super(AssessmentAdmin, self).get_queryset(request)
        else:
            # Regular faculty member can only see their assessments
            qs = super(AssessmentAdmin, self).get_queryset(request)
            return qs.filter(section__faculty=request.user)

    def save_model(self, request, obj, form, change):
        # Check if the user is a superuser
        if not request.user.is_superuser and obj.section.faculty != request.user:
            raise forms.ValidationError("You cannot assign assessments to a section you don't own.")
        super().save_model(request, obj, form, change)

    def has_module_permission(self, request):
        # Hide the course from the admin index page and sidebar
        return False

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('assessment', 'text', 'marks')
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
# admin.site.register(Question, QuestionAdmin)

# Override the verbose names dynamically in the admin interface
CourseLearningOutcome._meta.verbose_name = "CLO"
CourseLearningOutcome._meta.verbose_name_plural = "CLOs"

ProgramLearningOutcome._meta.verbose_name = "PLO"
ProgramLearningOutcome._meta.verbose_name_plural = "PLOs"

CustomUser._meta.verbose_name = "User"
CustomUser._meta.verbose_name_plural = "Users"

# Program._meta.verbose_name_plural = "Programs & Courses"