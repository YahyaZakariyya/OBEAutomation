from django.contrib import admin
from django import forms
from django.urls import reverse
from django.utils.html import format_html
from django.shortcuts import get_object_or_404

from obesystem.models import Section, Course, Program, Assessment


# Custom form to filter the program choices dynamically in Django admin
class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'course' in self.data:
            try:
                course_id = int(self.data.get('course'))
                course = Course.objects.get(id=course_id)
                self.fields['program'].queryset = course.programs.all()
            except (ValueError, Course.DoesNotExist):
                self.fields['program'].queryset = Program.objects.none()
        elif self.instance.pk and self.instance.course:
            self.fields['program'].queryset = self.instance.course.programs.all()
        else:
            self.fields['program'].queryset = Program.objects.none()

class SectionAdmin(admin.ModelAdmin):
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
    
    class Media:
        js = ('admin/js/dynamic_program.js',)  # Link to the custom JavaScript file


admin.site.register(Section, SectionAdmin)