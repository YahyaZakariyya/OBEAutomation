from django.contrib import admin
from django import forms
from django.urls import reverse
from django.shortcuts import get_object_or_404
from sections.models import Section
from assessments.models import Assessment
from guardian.shortcuts import get_objects_for_user
from guardian.admin import GuardedModelAdmin
from django.utils.translation import gettext_lazy as _

class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ['program', 'course', 'faculty', 'semester', 'section', 'batch', 'year', 'students', 'status']

    class Media:
        js = ('js/section_form.js',)  # Link to the custom JavaScript file

class SectionAdmin(GuardedModelAdmin):
    form = SectionForm

    list_display = ('course', 'semester', 'section', 'batch', 'year', 'faculty')
    list_filter = ('semester', 'batch', 'year')
    search_fields = ('course__name', 'faculty__username', 'faculty__first_name', 'faculty__last_name')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        # Filter based on object-level permissions
        return queryset.filter(pk__in=get_objects_for_user(
            request.user, 'sections.view_section', queryset
        ))

    def has_module_permission(self, request):
        return True
    
    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj:
            return request.user.has_perm('sections.view_section', obj)
        return True

    def change_view(self, request, object_id, form_url='', extra_context=None):
        section = get_object_or_404(Section, pk=object_id)
        extra_context = extra_context or {}
        extra_context['add_assessment_url'] = reverse('admin:%s_%s_add' % (
            Assessment._meta.app_label, Assessment._meta.model_name)) + f'?section={object_id}'
        extra_context['view_assessments_url'] = reverse('admin:%s_%s_changelist' % (
            Assessment._meta.app_label, Assessment._meta.model_name)) + f'?section__id__exact={object_id}'
        
        return super(SectionAdmin, self).change_view(request, object_id, form_url, extra_context)

admin.site.register(Section, SectionAdmin)

# Dynamic Sidebar Name Override
class DynamicSidebarMixin:
    def get_app_list(self, request, app_label=None):
        app_list = super().get_app_list(request, app_label)

        standard_result_url = ''
        obe_result_url = ''
        
        # Dynamically update the sidebar name for "Sections" based on user role
        for app in app_list:
            for model in app['models']:
                if model['object_name'] == 'Section':  # Match the model class name
                    if hasattr(request.user, 'role'):
                        if request.user.role == 'faculty':
                            standard_result_url = '/results/faculty-result-view/'
                            obe_result_url = '/results/faculty-obe-result-view/'
                            model['name'] = _("Assigned Courses")
                        elif request.user.role == 'student':
                            standard_result_url = '/results/student-result-view/'
                            # obe_result_url = 'results/faculty-obe-result-view/'
                            model['name'] = _("Enrolled Courses")
                        else:
                            model['name'] = _("Sections")

        # Add a custom menu item for "Custom Reports"
        custom_app_items = [{
            'name': 'Standard Results',         # Menu item name
            'app_label': 'general_result',      # Required for Jazzmin
            'object_name': 'GeneralResult',   # Identifier
            'admin_url': standard_result_url,  # Target URL
            'perms': {'view': True},          # Permission check
            'icon': 'fas fa-chart-line'       # Optional: FontAwesome icon
        }, {
            'name': 'OBE Result',         # Menu item name
            'app_label': 'obe_result',      # Required for Jazzmin
            'object_name': 'OBEResult',   # Identifier
            'admin_url': obe_result_url,  # Target URL
            'perms': {'view': True},          # Permission check
            'icon': 'fas fa-chart-line'       # Optional: FontAwesome icon
        },]

        # Add this menu under a "Custom Tools" app
        custom_app = {
            'name': 'Result App',       # App name in the sidebar
            'app_label': 'Results',  # Required
            'models': custom_app_items  # List of menu items
        }
        # In get_app_list or similar logic:
        app_list.append(custom_app)

        return app_list

# Apply the Mixin to the Default Admin Site
admin.site.__class__ = type('DynamicAdminSite', (DynamicSidebarMixin, admin.AdminSite), {})