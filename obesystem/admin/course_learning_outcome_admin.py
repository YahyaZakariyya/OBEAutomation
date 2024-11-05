from django.contrib import admin
from obesystem.models import CourseLearningOutcome

class CourseLearningOutcomeAdmin(admin.ModelAdmin):
    list_display = ('custom_number', 'custom_description')
    list_filter = ('course',)

    def custom_number(self, obj):
        return str(obj)
    custom_number.short_description = 'CLO #'

    def custom_description(self, obj):
        return obj.description
    custom_description.short_description = 'Description'

    def get_queryset(self, request):
        # Order CLOs by ascending CLO number
        qs = super().get_queryset(request)
        return qs.order_by('CLO')  # Ascending order by CLO number

    def has_module_permission(self, request):
        # Hide the course from the admin index page and sidebar
        return False

admin.site.register(CourseLearningOutcome, CourseLearningOutcomeAdmin)

# Override the verbose names dynamically in the admin interface
CourseLearningOutcome._meta.verbose_name = "CLO"
CourseLearningOutcome._meta.verbose_name_plural = "CLOs"