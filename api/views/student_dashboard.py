from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from programs.models import Program
from courses.models import Course
from sections.models import Section
from api.permissions import IsStudentUser

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsStudentUser])
def student_dashboard(request):
    # Get the logged-in student
    student = request.user

    # Fetch all available Programs (students can view all)
    programs = list(Program.objects.values("program_abbreviation", "program_title"))

    # Fetch Sections where the student is enrolled
    enrolled_sections = Section.objects.filter(students=student).values("id", "course__name", "semester", "section")

    available_courses = Course.objects.count()

    # API Response
    data = {
        "programs": programs,
        "courses": available_courses,
        "sections": list(enrolled_sections),
    }

    return Response(data)
