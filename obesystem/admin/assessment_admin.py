from django.contrib import admin
from django import forms
from obesystem.admin.question_admin import QuestionInline
from obesystem.models import Assessment, Section

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

admin.site.register(Assessment, AssessmentAdmin)