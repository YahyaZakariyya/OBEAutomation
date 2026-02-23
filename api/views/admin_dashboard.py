from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from programs.models import Program
from courses.models import Course
from sections.models import Section
from users.models import CustomUser
from api.permissions import IsAdminUser

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def admin_dashboard(request):

    data = {
        "programs": {
            "Undergraduate": Program.objects.filter(program_type="UG").count(),
            "Graduate": Program.objects.filter(program_type="GR").count(),
            "Postgraduate": Program.objects.filter(program_type="PG").count(),
            "Total": Program.objects.count(),
        },
        "courses": {
            program.program_abbreviation: program.courses.count()
            for program in Program.objects.all()
        },
        "sections": {
            "In Progress": Section.objects.filter(status="in_progress").count(),
            "Completed": Section.objects.filter(status="complete").count(),
            "Total": Section.objects.count(),
        },
        "users": {
            "Admins": CustomUser.objects.filter(role="admin").count(),
            "Faculty": CustomUser.objects.filter(role="faculty").count(),
            "Students": CustomUser.objects.filter(role="student").count(),
            "Total": CustomUser.objects.count(),
        },
    }
    data["courses"]["Total"] = Course.objects.count()

    return Response(data)
