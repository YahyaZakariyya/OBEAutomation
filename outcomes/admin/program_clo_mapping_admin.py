from django.contrib import admin
from django import forms
from outcomes.models import PloCloMapping

class ProgramCLOMappingForm(forms.ModelForm):
    class Meta:
        model = PloCloMapping
        fields = ['program', 'plo', 'course', 'clo', 'weightage']
    class Media:
        js = ('js/mappings.js',)

class ProgramCLOMappingAdmin(admin.ModelAdmin):
    form = ProgramCLOMappingForm
    list_display = ('program', 'course', 'clo', 'plo', 'weightage')
    list_filter = ('program', 'course')
    search_fields = ('program__name', 'course__name', 'clo__name', 'plo__name')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.order_by('program','course','clo')
    
admin.site.register(PloCloMapping, ProgramCLOMappingAdmin)

PloCloMapping._meta.verbose_name = "Mapping (CLO → PLO)"
PloCloMapping._meta.verbose_name_plural = "Mappings (CLO → PLO)"