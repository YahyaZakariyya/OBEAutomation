from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework.views import APIView
from users.models import CustomUser  # Import the custom user model
from programs.models import Program
from sections.models import Section
from courses.models import Course

class DashboardOverview(APIView):
    def get(self, request):
        programs = Program.objects.all()
        sections = Section.objects.all()
        courses = Course.objects.all()
        users = CustomUser.objects.all()  # Fetch all users
        admins = CustomUser.objects.filter(is_superuser=True)  # Assuming is_staff indicates admin users

        data = {
            'total_programs': programs.count(),
            'active_programs': programs.filter(is_active=True).count(),  # Count active programs
            'total_sections': sections.count(),
            'active_sections': sections.filter(is_active=True, status='in_progress').count(),  # Count active sections
            'total_courses': courses.count(),
            'active_courses': courses.filter(is_active=True).count(),  # Count active courses
            'total_users': users.count(),
            'total_admins': admins.count(),
        }

        return Response(data)
 
    # def get(self, request):
    #     sections = Section.objects.all().values('program', 'course', 'faculty', 'semester', 'section', 'batch', 'year', 'students', 'status')
    #     dataa = list(sections)
    #     return JsonResponse(dataa)
