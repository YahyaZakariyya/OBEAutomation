from django.contrib import admin
from django.utils.html import format_html
from obesystem.models import Course
from django.http import JsonResponse


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
        return ", ".join([program.name for program in obj.programs.all()])
    display_programs.short_description = "Programs"  # This will show "Programs" in the admin list view

    def view_clos(self, obj):
        url = f"/obesystem/courselearningoutcome/?course__id__exact={obj.id}"
        return format_html('<a class="btn btn-primary" href="{}">View CLOs</a>', url)
    view_clos.short_description = "View CLOs"
    view_clos.allow_tags = True  # Ensures the HTML is rendered correctly

def get_programs(request):
    course_id = request.GET.get('course_id')
    programs = []
    if course_id:
        try:
            course = Course.objects.get(id=course_id)
            programs = [{'id': program.id, 'name': program.name} for program in course.programs.all()]
        except Course.DoesNotExist:
            pass
    return JsonResponse(programs, safe=False)


admin.site.register(Course, CourseAdmin)