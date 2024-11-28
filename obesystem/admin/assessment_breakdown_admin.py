from django.contrib import admin
from django.core.exceptions import ValidationError
from django import forms
from obesystem.models import AssessmentBreakdown

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
class AssessmentBreakdownAdmin(admin.ModelAdmin):
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

    def has_add_permission(self, request):
        # Restrict add permission to prevent multiple entries per section
        return super().has_add_permission(request)

    def has_change_permission(self, request, obj=None):
        # Allow change permission only if the object exists
        return super().has_change_permission(request, obj)

    def save_model(self, request, obj, form, change):
        # Additional checks if needed before saving
        super().save_model(request, obj, form, change)
