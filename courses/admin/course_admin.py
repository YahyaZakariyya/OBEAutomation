from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from courses.models import Course

class CourseAdmin(admin.ModelAdmin):
    list_display = ('custom_course_name', 'credit_hours', 'display_programs', 'view_clos')
    list_filter = ('programs',)  # Use the ManyToManyField name here
    search_fields = ('name',)

    def custom_course_name(self, obj):
        return obj.name
    custom_course_name.short_description = "Course Title"
    custom_course_name.admin_order_field = "name"

    def display_programs(self, obj):
        # Joining all program names associated with the course
        return ", ".join([program.program_abbreviation for program in obj.programs.all()])
    display_programs.short_description = "Programs"  # This will show "Programs" in the admin list view

    def view_clos(self, obj):
        url = reverse('admin:outcomes_courselearningoutcome_changelist') + f"?course__id__exact={obj.id}"
        return format_html('<a class="btn btn-sm btn-dark" href="{}">CLOs</a>', url)
    view_clos.short_description = "View CLOs"
    view_clos.allow_tags = True  # Ensures the HTML is rendered correctly

admin.site.register(Course, CourseAdmin)