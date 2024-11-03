from django.contrib import admin
from obesystem.models import CourseLearningOutcome

class CourseLearningOutcomeAdmin(admin.ModelAdmin):
    list_display = ('course', 'description')
    list_filter = ('course',)
    search_fields = ('description',)
    filter_horizontal = ('mapped_to_PLO',)

    def save_model(self, request, obj, form, change):
        # Save the instance first
        super().save_model(request, obj, form, change)
        # Save the ManyToMany relations
        form.save_m2m()

    def save_related(self, request, form, formsets, change):
        # Save related many-to-many data after the main form is saved
        form.save_m2m()
        super().save_related(request, form, formsets, change)

    def has_module_permission(self, request):
        # Hide the course from the admin index page and sidebar
        return False

admin.site.register(CourseLearningOutcome, CourseLearningOutcomeAdmin)
# Override the verbose names dynamically in the admin interface
CourseLearningOutcome._meta.verbose_name = "CLO"
CourseLearningOutcome._meta.verbose_name_plural = "CLOs"