from django.shortcuts import render
from obesystem.models import CourseLearningOutcome, ProgramLearningOutcome, Section, Program
from obesystem.utils.calculations import calculate_clo_attainment, calculate_plo_attainment
from django.contrib.admin.sites import site
from django.contrib.auth.decorators import login_required
from guardian.shortcuts import get_objects_for_user


def clo_plo_report_view(request):
    student_id = request.GET.get('student_id')
    section_id = request.GET.get('section_id')

    # Get all CLOs and PLOs for the section
    clos = CourseLearningOutcome.objects.filter(course__sections__id=section_id)
    plos = ProgramLearningOutcome.objects.filter(program__sections__id=section_id)

    # Calculate attainments
    clo_results = [
        {"name": clo.heading, "attainment": calculate_clo_attainment(clo, student_id)}
        for clo in clos
    ]
    plo_results = [
        {"name": plo.heading, "attainment": calculate_plo_attainment(plo, student_id)}
        for plo in plos
    ]

    return render(request, "obesystem/student_clo_performance.html", {"clos": clo_results, "plos": plo_results})


@login_required
def student_clo_performance_view(request):
    """
    Renders the student CLO performance page for the logged-in student.
    """
    student = request.user  # Get the logged-in student

    # Fetch only the sections visible to this student
    sections = Section.objects.filter(students=student)  # Assuming a ManyToManyField 'students' in Section model

    context = {
        **site.each_context(request),  # Includes admin context like available_apps
        "sections": sections,
        "student_id": student.id,  # Pass student ID for frontend reference
    }
    return render(request, "obesystem/student_clo_performance.html", context)

@login_required
def faculty_clo_dashboard(request):
    """
    Renders the faculty CLO performance dashboard for the logged-in faculty member.
    """
    faculty = request.user  # Get the logged-in faculty member

    # Fetch only sections visible to this faculty member (using object-level permissions if applicable)
    faculty_sections = get_objects_for_user(faculty, 'view_section', Section)

    # Fetch all programs for filtering purposes
    programs = Program.objects.all()

    context = {
        **site.each_context(request),  # Includes admin context like available_apps
        'sections': faculty_sections,
        'programs': programs,
    }

    return render(request, 'obesystem/faculty_clo_analysis.html', context)

@login_required
def faculty_result_view(request):
    """
    Renders the faculty CLO performance dashboard for the logged-in faculty member.
    """
    faculty = request.user  # Get the logged-in faculty member

    # Fetch only sections visible to this faculty member (using object-level permissions if applicable)
    faculty_sections = get_objects_for_user(faculty, 'view_section', Section)

    context = {
        **site.each_context(request),  # Includes admin context like available_apps
        'sections': faculty_sections,
    }

    return render(request, 'obesystem/faculty_result.html', context)

@login_required
def student_result_view(request):
    student = request.user  # Get the logged-in faculty member

    # Fetch only sections visible to this student (using object-level permissions if applicable)
    user_sections = get_objects_for_user(student, 'view_section', Section)

    context = {
        **site.each_context(request),  # Includes admin context like available_apps
        'sections': user_sections,
    }

    return render(request, 'obesystem/student_result.html', context)