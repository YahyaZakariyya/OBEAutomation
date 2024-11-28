from django.contrib import admin
from obesystem.models import ProgramLearningOutcome

class ProgramLearningOutcomeAdmin(admin.ModelAdmin):
    list_display = ('custom_number', 'custom_description', 'weightage_with_percentage')
    list_filter = ('program',)

    def custom_number(self, obj):
        return str(obj)
    custom_number.short_description = 'PLO #'

    def custom_description(self, obj):
        return obj.description
    custom_description.short_description = 'Description'

    def weightage_with_percentage(self, obj):
        return f"{obj.weightage}%"
    weightage_with_percentage.short_description = 'Weightage'

    def get_queryset(self, request):
        # Order PLOs by ascending PLO number
        qs = super().get_queryset(request)
        return qs.order_by('PLO')  # Ascending order by PLO number

    def has_module_permission(self, request):
        # Hide the course from the admin index page and sidebar
        return False
    
admin.site.register(ProgramLearningOutcome, ProgramLearningOutcomeAdmin)

ProgramLearningOutcome._meta.verbose_name = "PLO"
ProgramLearningOutcome._meta.verbose_name_plural = "PLOs"