from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from programs.models import Program
from users.models import CustomUser
from django.template.response import TemplateResponse

class ProgramAdmin(admin.ModelAdmin):
    list_display = ('program_abbreviation', 'program_incharge', 'program_type', 'view_courses', 'view_plos')
    search_fields = ('program_abbreviation',)

    # def changelist_view(self, request, extra_context=None):
    #     # Step 1: Let Django handle filters, search, and pagination first
    #     response = super().changelist_view(request, extra_context)
    #     if request.method == "GET" and hasattr(response, 'context_data'):
    #         # Step 2: Fetch the original queryset from the context
    #         queryset = response.context_data['cl'].queryset

    #         # Step 3: Dynamically group queryset by `program_type`
    #         distinct_values = queryset.values_list('program_type', flat=True).distinct()
    #         grouped_tables = {
    #             value: queryset.filter(program_type=value) for value in distinct_values
    #         }

    #         # Step 4: Add grouped tables to the context
    #         response.context_data['grouped_tables'] = grouped_tables

    #     return response

    def view_courses(self, obj):
        url = reverse('admin:courses_course_changelist') + f"?programs__id__exact={obj.id}"
        return format_html('<a class="btn btn-sm btn-dark" href="{}">Courses</a>', url)
    
    view_courses.short_description = "View Courses"
    view_courses.allow_tags = True  # Ensures the HTML is rendered correctly

    def view_plos(self, obj):
        url = reverse('admin:outcomes_programlearningoutcome_changelist') + f"?programs__id__exact={obj.id}"
        return format_html('<a class="btn btn-sm btn-dark" href="{}">PLOs</a>', url)
    
    view_plos.short_description = "View PLOs"
    view_plos.allow_tags = True  # Ensures the HTML is rendered correctly

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "hod" and not request.user.is_superuser:
            kwargs["queryset"] = CustomUser.objects.filter(role='head_of_department')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(Program, ProgramAdmin)