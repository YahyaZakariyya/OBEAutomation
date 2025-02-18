from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from programs.models import Program
from courses.models import Course
from sections.models import Section

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def faculty_dashboard(request):
    # Get the logged-in student
    faculty = request.user
    if faculty.role != 'faculty':
        return Response({"error": "Unauthorized"}, status=403)

    # Fetch all available Programs (students can view all)
    programs = list(Program.objects.values("program_abbreviation", "program_title"))

    # Fetch Sections where the student is enrolled
    assigned_courses = Section.objects.filter(faculty=faculty).values("id", "course__name", "semester", "section")

    available_courses = Course.objects.count()

    # API Response
    data = {
        "programs": programs,
        "courses": available_courses,
        "sections": list(assigned_courses),
    }

    return Response(data)