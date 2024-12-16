from django.contrib import admin
from django import forms
from django.http import JsonResponse
from django.urls import path
from outcomes.models import ProgramLearningOutcome, CourseLearningOutcome, PloCloMapping

# Define the AJAX view functions
def get_plos(request):
    program_id = request.GET.get('program_id')
    plos = ProgramLearningOutcome.objects.filter(program_id=program_id)
    data = [{'id': plo.id, 'name': plo.heading} for plo in plos]
    return JsonResponse(data, safe=False)

def get_clos(request):
    course_id = request.GET.get('course_id')
    clos = CourseLearningOutcome.objects.filter(course_id=course_id)
    data = [{'id': clo.id, 'name': clo.description} for clo in clos]
    return JsonResponse(data, safe=False)

class ProgramCLOMappingForm(forms.ModelForm):
    class Meta:
        model = PloCloMapping
        fields = ['program', 'course', 'clo', 'plo', 'weightage']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filter CLOs based on the selected course
        if 'course' in self.data:
            try:
                course_id = int(self.data.get('course'))
                self.fields['clo'].queryset = CourseLearningOutcome.objects.filter(course_id=course_id)
            except (ValueError, TypeError):
                self.fields['clo'].queryset = CourseLearningOutcome.objects.none()
        elif self.instance.pk and self.instance.course:
            self.fields['clo'].queryset = CourseLearningOutcome.objects.filter(course=self.instance.course)
        else:
            self.fields['clo'].queryset = CourseLearningOutcome.objects.none()
        
        # Filter PLOs based on the selected program
        if 'program' in self.data:
            try:
                program_id = int(self.data.get('program'))
                self.fields['plo'].queryset = ProgramLearningOutcome.objects.filter(program_id=program_id)
            except (ValueError, TypeError):
                self.fields['plo'].queryset = ProgramLearningOutcome.objects.none()
        elif self.instance.pk and self.instance.program:
            self.fields['plo'].queryset = ProgramLearningOutcome.objects.filter(program=self.instance.program)
        else:
            self.fields['plo'].queryset = ProgramLearningOutcome.objects.none()

class ProgramCLOMappingAdmin(admin.ModelAdmin):
    form = ProgramCLOMappingForm
    list_display = ('program', 'course', 'clo', 'plo', 'weightage')
    list_filter = ('program', 'course')
    search_fields = ('program__name', 'course__name', 'clo__name', 'plo__name')

    class Media:
        js = ('admin/js/program_clo_mapping.js',)  # Path to your custom JavaScript file

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('get_plos/', self.admin_site.admin_view(get_plos), name='get_plos'),
            path('get_clos/', self.admin_site.admin_view(get_clos), name='get_clos'),
        ]
        return custom_urls + urls
    
admin.site.register(PloCloMapping, ProgramCLOMappingAdmin)

PloCloMapping._meta.verbose_name = "Mapping (CLO → PLO)"
PloCloMapping._meta.verbose_name_plural = "Mappings (CLO → PLO)"