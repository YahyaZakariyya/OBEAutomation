from django.shortcuts import render
from sections.models import Section
from django.contrib.admin.sites import site
from django.contrib.auth.decorators import login_required
from guardian.shortcuts import get_objects_for_user

@login_required
def faculty_obe_result_view(request):
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

    return render(request, 'results/faculty_obe_result.html', context)