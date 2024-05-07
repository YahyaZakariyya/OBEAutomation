from django.contrib import admin
from .models import *


# class AssessmentAdmin(admin.ModelAdmin):
#     def get_queryset(self, request):
#         qs = super().get_queryset(request)
#         if request.user.is_superuser:
#             return qs  # Superuser gets to see all records
#         return qs.filter(created_by__user=request.user)  # Faculty sees only their assessments

#     def has_change_permission(self, request, obj=None):
#         if obj is not None and not request.user.is_superuser:
#             return obj.created_by.user == request.user
#         return True

#     def has_delete_permission(self, request, obj=None):
#         if obj is not None and not request.user.is_superuser:
#             return obj.created_by.user == request.user
#         return True

# admin.site.register(Assessment, AssessmentAdmin)

class CourseAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs  # Superuser gets to see all records
        elif request.user.groups.filter(name='HOD').exists():
            return qs.filter(program__hod__user=request.user)
        return qs  # Modify or restrict further based on your rules

admin.site.register(Course, CourseAdmin)


class CourseLearningOutcomeAdmin(admin.ModelAdmin):
    list_display = ('course', 'description')
    filter_horizontal = ('plos',)

admin.site.register(CourseLearningOutcome, CourseLearningOutcomeAdmin)

# Register your models here.
admin.site.register(Program)
admin.site.register(ProgramLearningOutcome)
# admin.site.register(Course)
# admin.site.register(CourseLearningOutcome)
admin.site.register(Section)
# admin.site.register(Assessment)
admin.site.register(Question)
admin.site.register(Director)
admin.site.register(Faculty)
admin.site.register(HeadOfDepartment)