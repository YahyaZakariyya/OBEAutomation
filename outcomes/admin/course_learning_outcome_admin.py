from django.contrib import admin
from outcomes.models import CourseLearningOutcome

class CourseLearningOutcomeAdmin(admin.ModelAdmin):
    list_display = ('course','custom_number', 'heading', 'description', 'weightage')
    list_filter = ('course',)
    show_full_result_count = False

    def custom_number(self, obj):
        return f"CLO {obj.CLO}"
    custom_number.short_description = 'CLO #'

    def custom_description(self, obj):
        return obj.description
    custom_description.short_description = 'Description'

    def get_queryset(self, request):
        # Order CLOs by ascending CLO number
        qs = super().get_queryset(request)
        return qs.order_by('course','CLO')  # Ascending order by CLO number

    def has_module_permission(self, request):
        # Hide the course from the admin index page and sidebar
        return True

admin.site.register(CourseLearningOutcome, CourseLearningOutcomeAdmin)

# Override the verbose names dynamically in the admin interface
CourseLearningOutcome._meta.verbose_name = "CLO"
CourseLearningOutcome._meta.verbose_name_plural = "CLOs"