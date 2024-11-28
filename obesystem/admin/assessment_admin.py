from django.contrib import admin
from django import forms
from obesystem.admin.question_admin import QuestionInline
from obesystem.models import Assessment, Section, Question
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.urls import path
from guardian.shortcuts import get_objects_for_user
from guardian.admin import GuardedModelAdmin

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

    # def get_urls(self):
    #     urls = super().get_urls()
    #     custom_urls = [
    #         path(
    #             'fetch-inline-rows/',
    #             self.admin_site.admin_view(self.fetch_inline_rows),
    #             name='fetch-inline-rows'
    #         ),
    #     ]
    #     return custom_urls + urls

    # def fetch_inline_rows(self, request):
    #     """Endpoint to fetch new inline rows via AJAX."""
    #     template_name = "admin/edit_inline/tabular.html"
    #     context = {
    #         "inline_admin_formset": self.get_inline_instances(request, None)[0].get_formset(
    #             None, change=False
    #         ),
    #     }
    #     rendered = render_to_string(template_name, context, request=request)
    #     return JsonResponse({"html": rendered})

class AssessmentAdmin(GuardedModelAdmin):
    form = AssessmentForm
    # inlines = [QuestionInline]
    
    # def get_queryset(self, request):
    #     """
    #     Restrict queryset to Assessment related to Sections
    #     the user has permissions for.
    #     """
    #     queryset = super().get_queryset(request)
    #     if request.user.is_superuser:
    #         return queryset
    #     # Get sections the user has permission to view
    #     sections = get_objects_for_user(request.user, 'obesystem.view_section')
    #     # Filter Assessment by those sections
    #     return queryset.filter(section__in=sections)

    def get_queryset(self, request):
        """
        Restrict queryset to Assessments the user has permissions for.
        """
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        return queryset.filter(
            pk__in=get_objects_for_user(request.user, 'obesystem.view_assessment', queryset)
        )

    def has_module_permission(self, request):
        return True
    
    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj:
            return request.user.has_perm('obesystem.view_assessment', obj)
        return True
    
    def has_add_permission(self, request, obj=None):
        """
        Allow faculty to add Assessment if they have the add permission
        for the related Section.
        """
        if obj is None:  # For the changelist view
            return True
        # Check if the user has the required permission for the related section
        print(request.user.has_perm('obesystem.add_assessment', obj), "Add Permission")
        return request.user.has_perm('obesystem.add_assessment', obj)

    def has_change_permission(self, request, obj=None):
        """
        Allow faculty to change Assessment if they have the change permission
        for the related Section.
        """
        if obj is None:  # For the changelist view
            return True
        # Check if the user has the required permission for the related section
        print(request.user.has_perm('obesystem.add_assessment', obj), "Change Permission")
        return request.user.has_perm('obesystem.change_assessment', obj)
    
    def has_delete_permission(self, request, obj=None):
        """
        Allow faculty to delete Assessments if they have delete permission
        for the related section.
        """
        if obj is None:  # For the changelist view
            print("Delete IF")
            return True
        print(request.user.has_perm('obesystem.delete_assessment', obj))
        return request.user.has_perm('obesystem.delete_assessment', obj)
    
    # def get_model_perms(self, request):
    #     """
    #     Return the dict of permissions for this model. Hide the "Add" button
    #     if the user doesn't have the add permission.
    #     """
    #     perms = super().get_model_perms(request)
    #     if not self.has_add_permission(request):
    #         perms['add'] = False
    #     return perms


admin.site.register(Assessment, AssessmentAdmin)