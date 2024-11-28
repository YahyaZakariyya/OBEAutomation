from django.contrib import admin
from django import forms
from obesystem.admin.question_admin import QuestionInline
from obesystem.models import Assessment, Section, Question
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.urls import path

class AssessmentForm(forms.ModelForm):
    class Meta:
        model = Assessment
        fields = ['title', 'section', 'date', 'type', 'weightage']

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

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'fetch-inline-rows/',
                self.admin_site.admin_view(self.fetch_inline_rows),
                name='fetch-inline-rows'
            ),
        ]
        return custom_urls + urls

    def fetch_inline_rows(self, request):
        """Endpoint to fetch new inline rows via AJAX."""
        template_name = "admin/edit_inline/tabular.html"
        context = {
            "inline_admin_formset": self.get_inline_instances(request, None)[0].get_formset(
                None, change=False
            ),
        }
        rendered = render_to_string(template_name, context, request=request)
        return JsonResponse({"html": rendered})

class AssessmentAdmin(admin.ModelAdmin):
    form = AssessmentForm
    inlines = [QuestionInline]

    def save_related(self, request, form, formsets, change):
        """
        Override save_related to ensure M2M fields (like 'clo') are handled after the main object is saved.
        """
        # Save the parent object and inlines
        super().save_related(request, form, formsets, change)

        # Iterate through formsets to save M2M fields for Question objects
        for formset in formsets:
            if formset.model == Question:
                for inline_form in formset.forms:
                    if inline_form.instance.pk:  # Ensure the object has been saved
                        inline_form.save_m2m()  # Save M2M relationships (CLOs)

    # def get_form(self, request, obj=None, **kwargs):
    #     form_class = super().get_form(request, obj, **kwargs)
    #     # Passing the user through kwargs
    #     class FormWithUser(form_class):
    #         def __init__(self, *args, **kwargs):
    #             kwargs['user'] = request.user
    #             super(FormWithUser, self).__init__(*args, **kwargs)

    #     return FormWithUser
    
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

    # def has_module_permission(self, request):
    #     # Hide the course from the admin index page and sidebar
    #     return False

admin.site.register(Assessment, AssessmentAdmin)