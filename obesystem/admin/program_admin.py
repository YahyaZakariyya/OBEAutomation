from django.contrib import admin
from django.utils.html import format_html
from obesystem.models import Program, CustomUser

class ProgramAdmin(admin.ModelAdmin):
    list_display = ('custom_program_name', 'custom_hod_name', 'view_courses', 'view_plos')
    search_fields = ('name',)

    def custom_program_name(self, obj):
        return obj.name
    custom_program_name.short_description = "Programs"
    custom_program_name.admin_order_field = "name"

    def custom_hod_name(self, obj):
        return obj.hod
    custom_hod_name.short_description = "Head of Department"
    custom_hod_name.admin_order_field = "hod"

    def view_courses(self, obj):
        url = f"/obesystem/course/?program__id={obj.id}"
        return format_html('<a class="btn btn-primary" href="{}">View Courses</a>', url)
    
    view_courses.short_description = "View Courses"
    view_courses.allow_tags = True  # Ensures the HTML is rendered correctly

    def view_plos(self, obj):
        url = f"/obesystem/programlearningoutcome/?program__id__exact={obj.id}"
        return format_html('<a class="btn btn-primary" href="{}">View PLOs</a>', url)
    
    view_plos.short_description = "View PLOs"
    view_plos.allow_tags = True  # Ensures the HTML is rendered correctly

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "hod" and not request.user.is_superuser:
            kwargs["queryset"] = CustomUser.objects.filter(role='head_of_department')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(Program, ProgramAdmin)
