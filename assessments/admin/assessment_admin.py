from django.contrib import admin
from assessments.models import Assessment
from sections.models import Section
from guardian.shortcuts import get_objects_for_user
from guardian.admin import GuardedModelAdmin
from .question_admin import QuestionInline
from django.utils.html import format_html
from django.urls import reverse

class AssessmentAdmin(GuardedModelAdmin):
    inlines = [QuestionInline]
    
    list_display = ['title', 'section', 'date', 'type', 'weightage', 'manage_marks_button']
    fields = ['title', 'section', 'date', 'type', 'weightage']
    
    def changelist_view(self, request, extra_context=None):
        # Pass the request to a custom attribute
        self.current_request = request
        return super().changelist_view(request, extra_context)
    
    def manage_marks_button(self, obj):
        if obj:  # Ensure obj is not None
            request = getattr(self, 'current_request', None)
            if request and self.has_change_permission(request, obj):
                url = reverse('edit_scores') + f'?id={obj.id}'
                return format_html('<a class="btn btn-sm btn-primary" href="{}" target="_blank">Manage Marks</a>', url)
            else:
                url = reverse('view_scores') + f'?assessment_id={obj.id}&student_id={request.user.id}'
                return format_html('<a href="{}">View Marks</a>', url)
        return "-"  # Return a default placeholder if obj is None

    manage_marks_button.short_description = 'Manage/View Marks'
    manage_marks_button.allow_tags = True
        
    def get_form(self, request, obj=None, **kwargs):
        """
        Customize the form to filter sections based on the user's permissions.
        """
        form = super().get_form(request, obj, **kwargs)
        
        # Check if the 'section' field exists in the form
        if 'section' in form.base_fields:
            # Superusers can see all sections
            if request.user.is_superuser:
                form.base_fields['section'].queryset = Section.objects.all()
            else:
                # Faculty members can only see sections they have `view_section` permission for
                allowed_sections = get_objects_for_user(request.user, 'sections.view_section', klass=Section)
                form.base_fields['section'].queryset = allowed_sections
        
        return form

    def get_queryset(self, request):
        """
        Restrict queryset to Assessments the user has permissions for.
        """
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        return queryset.filter(
            pk__in=get_objects_for_user(request.user, 'assessments.view_assessment', queryset)
        )

    def has_module_permission(self, request):
        return True

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj:
            return request.user.has_perm('assessments.view_assessment', obj)
        return True

    def has_add_permission(self, request, obj=None):
        """
        Allow faculty to add Assessment only if they have the `can_add_assessment` permission for the related Section.
        """
        if obj is None:  # For the changelist or adding a new object
            # Ensure the user has add permission for at least one section
            allowed_sections = get_objects_for_user(request.user, 'sections.can_add_assessment', klass=Section)
            return allowed_sections.exists()

        # Check if the user has the required permission for the related section of this object
        return request.user.has_perm('sections.can_add_assessment', obj.section)

    def has_change_permission(self, request, obj=None):
        """
        Allow faculty to change Assessment if they have the change permission
        for the related Section.
        """
        if obj is None:  # For the changelist view
            return True
        # Check if the user has the required permission for the related section
        return request.user.has_perm('assessments.change_assessment', obj)

    def has_delete_permission(self, request, obj=None):
        """
        Allow faculty to delete Assessments if they have delete permission
        for the related section.
        """
        if obj is None:  # For the changelist view
            return True
        return request.user.has_perm('assessments.delete_assessment', obj)
    
    class Media:
        js = ('js/assessment_clo_filter.js',)  # Add the JS file

admin.site.register(Assessment, AssessmentAdmin)