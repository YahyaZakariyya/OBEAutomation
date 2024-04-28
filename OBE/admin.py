from django.contrib import admin
from .models import Program, PLO, Course, CLO, Assessment

# Register your models here.
admin.site.register(Program)
admin.site.register(PLO)
admin.site.register(Course)
admin.site.register(CLO)
admin.site.register(Assessment)