from django.contrib import admin
from obesystem.models import Assessment, Section
from guardian.shortcuts import get_objects_for_user
from guardian.admin import GuardedModelAdmin
from obesystem.admin.question_admin import QuestionInline
from django.utils.html import format_html

class AssessmentAdmin(admin.ModelAdmin):
    inlines = [QuestionInline]

    list_display = ['title', 'section', 'date', 'type', 'weightage', 'manage_marks_button']
    fields = ['title', 'section', 'date', 'type', 'weightage']
    
    def manage_marks_button(self, obj):
        return format_html('<a href="/app/assessment?id={}" target="_blank">Edit Scores</a>', obj.id)

    manage_marks_button.short_description = 'Manage Marks'  # Column header in admin
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
                allowed_sections = get_objects_for_user(request.user, 'obesystem.view_section', klass=Section)
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
        Allow faculty to add Assessment only if they have the `can_add_assessment` permission
        for the related Section.
        """
        if obj is None:  # For the changelist or adding a new object
            # Ensure the user has add permission for at least one section
            allowed_sections = get_objects_for_user(request.user, 'obesystem.can_add_assessment', klass=Section)
            return allowed_sections.exists()

        # Check if the user has the required permission for the related section of this object
        return request.user.has_perm('obesystem.can_add_assessment', obj.section)

    def has_change_permission(self, request, obj=None):
        """
        Allow faculty to change Assessment if they have the change permission
        for the related Section.
        """
        if obj is None:  # For the changelist view
            return True
        # Check if the user has the required permission for the related section
        return request.user.has_perm('obesystem.change_assessment', obj)
    
    def has_delete_permission(self, request, obj=None):
        """
        Allow faculty to delete Assessments if they have delete permission
        for the related section.
        """
        if obj is None:  # For the changelist view
            return True
        return request.user.has_perm('obesystem.delete_assessment', obj)
    
admin.site.register(Assessment, AssessmentAdmin)