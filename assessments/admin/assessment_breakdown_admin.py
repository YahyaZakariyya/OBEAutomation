from django.contrib import admin
from django.core.exceptions import ValidationError
from django import forms
from assessments.models import AssessmentBreakdown
from guardian.shortcuts import get_objects_for_user
from guardian.admin import GuardedModelAdmin

# Custom form for validation in admin
class AssessmentBreakdownForm(forms.ModelForm):
    class Meta:
        model = AssessmentBreakdown
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        
        # Calculate total weightage
        total_weightage = (
            cleaned_data.get('assignment_weightage', 0) +
            cleaned_data.get('quiz_weightage', 0) +
            cleaned_data.get('lab_weightage', 0) +
            cleaned_data.get('mid_weightage', 0) +
            cleaned_data.get('final_weightage', 0) +
            cleaned_data.get('project_weightage', 0)
        )
        
        # Ensure total weightage equals 100
        if total_weightage != 100:
            raise ValidationError("The total weightage must be exactly 100%.")

        return cleaned_data

# Admin configuration for AssessmentBreakdown
@admin.register(AssessmentBreakdown)
class AssessmentBreakdownAdmin(GuardedModelAdmin):
    form = AssessmentBreakdownForm  # Use the custom form with validation
    list_display = ('section', 'assignment_weightage', 'quiz_weightage', 'lab_weightage', 'mid_weightage', 'final_weightage', 'project_weightage')
    list_filter = ('section',)
    search_fields = ('section__name',)  # Assumes 'name' field on Section model

    fieldsets = (
        (None, {
            'fields': (
                'section', 
                'assignment_weightage', 
                'quiz_weightage', 
                'lab_weightage', 
                'mid_weightage', 
                'final_weightage', 
                'project_weightage',
            )
        }),
    )

    def get_queryset(self, request):
        """
        Restrict queryset to AssessmentBreakdowns related to Sections
        the user has permissions for.
        """
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        # Get sections the user has permission to view
        sections = get_objects_for_user(request.user, 'sections.view_section')
        # Filter AssessmentBreakdown by those sections
        return queryset.filter(section__in=sections)

    def has_module_permission(self, request):
        return True
    
    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj:
            return request.user.has_perm('assessments.view_assessmentbreakdown', obj)
        return True
    
    def has_add_permission(self, request):
        """
        Disable the ability to manually add AssessmentBreakdown from the everyone.
        """
        return False

    def has_change_permission(self, request, obj=None):
        """
        Allow faculty to change AssessmentBreakdown if they have the change permission
        for the related Section.
        """
        if obj is None:  # For the changelist view
            return True
        # Check if the user has the required permission for the related section
        return request.user.has_perm('assessments.change_assessmentbreakdown', obj)
    
    def has_delete_permission(self, request, obj=None):
        """
        No one can delete AssessmentBreakdowns.
        """
        if request.user.is_superuser:
            return True
        return False

    def save_model(self, request, obj, form, change):
        # Additional checks if needed before saving
        super().save_model(request, obj, form, change)
