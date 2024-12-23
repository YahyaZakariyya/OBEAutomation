# from django.http import JsonResponse
# from sections.models import Section
# from guardian.admin import GuardedModelAdmin
# from sections import section_admin

# def get(self, request):
#         sections = Section.objects.all().values('program', 'course', 'faculty', 'semester', 'section', 'batch', 'year', 'students', 'status')
#         data = list(sections)
#         return JsonResponse(data, safe=False)