from rest_framework.response import Response
from rest_framework.decorators import api_view
from programs.models import Program
from courses.models import Course
from sections.models import Section
from users.models import CustomUser

@api_view(['GET'])
def admin_dashboard(request):
    # ✅ Programs Overview (Total by Type)
    program_counts = {
        "Undergraduate": Program.objects.filter(program_type="UG").count(),
        "Graduate": Program.objects.filter(program_type="GR").count(),
        "Postgraduate": Program.objects.filter(program_type="PG").count(),
        "Total": Program.objects.count(),
    }

    # ✅ Courses Overview (Total per Program)
    course_counts = {
        program.program_abbreviation: program.courses.count()
        for program in Program.objects.all()
    }
    course_counts["Total"] = Course.objects.count()

    # ✅ Sections Overview (In Progress & Completed)
    section_counts = {
        "In Progress": Section.objects.filter(status="in_progress").count(),
        "Completed": Section.objects.filter(status="complete").count(),
        "Total": Section.objects.count(),
    }

    # ✅ User Management (Total by Role)
    user_counts = {
        "Admins": CustomUser.objects.filter(role="admin").count(),
        "Faculty": CustomUser.objects.filter(role="faculty").count(),
        "Students": CustomUser.objects.filter(role="student").count(),
        "Total": CustomUser.objects.count(),
    }

    # ✅ CLO Performance (Static Link)
    clo_performance = {
        "report_link": "/clo-performance/",
    }

    # ✅ System Configurations (Static Links)
    system_configurations = {
        "configure_clos": "/configurations/clo",
        "program_weightings": "/configurations/weightings",
    }

    # 🔥 Response Data
    data = {
        "programs": program_counts,
        "courses": course_counts,
        "sections": section_counts,
        "users": user_counts,
        "clo_performance": clo_performance,
        "system_configurations": system_configurations,
    }

    return Response(data)
