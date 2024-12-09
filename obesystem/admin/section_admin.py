from django.contrib import admin
from django import forms
from django.http import JsonResponse
from django.urls import reverse, path
from django.utils.html import format_html
from django.shortcuts import get_object_or_404
from obesystem.models import Section, Course, Assessment
from guardian.shortcuts import get_objects_for_user
from guardian.admin import GuardedModelAdmin

def get_courses(request):
    program_id = request.GET.get('program_id')
    if program_id:
        courses = Course.objects.filter(programs__id=program_id)
        data = [{'id': course.id, 'name': course.name} for course in courses]
        return JsonResponse(data, safe=False)
    return JsonResponse([], safe=False)  # Return an empty list if no program is selected

class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ['program', 'course', 'faculty', 'semester', 'section', 'batch', 'year', 'students', 'status']

class SectionAdmin(GuardedModelAdmin):
    form = SectionForm

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
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        # Filter based on object-level permissions
        return queryset.filter(pk__in=get_objects_for_user(
            request.user, 'obesystem.view_section', queryset
        ))

    def has_module_permission(self, request):
        return True
    
    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj:
            return request.user.has_perm('obesystem.view_section', obj)
        return True

    def change_view(self, request, object_id, form_url='', extra_context=None):
        section = get_object_or_404(Section, pk=object_id)
        extra_context = extra_context or {}
        extra_context['add_assessment_url'] = reverse('admin:%s_%s_add' % (
            Assessment._meta.app_label, Assessment._meta.model_name)) + f'?section={object_id}'
        extra_context['view_assessments_url'] = reverse('admin:%s_%s_changelist' % (
            Assessment._meta.app_label, Assessment._meta.model_name)) + f'?section__id__exact={object_id}'
        
        return super(SectionAdmin, self).change_view(request, object_id, form_url, extra_context)
    
    class Media:
        js = ('admin/js/dynamic_program.js',)  # Link to the custom JavaScript file

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('get-courses/', self.admin_site.admin_view(get_courses), name='get_courses'),
        ]
        return custom_urls + urls

admin.site.register(Section, SectionAdmin)