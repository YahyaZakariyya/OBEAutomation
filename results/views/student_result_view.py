from django.shortcuts import render
from sections.models import Section
from django.contrib.admin.sites import site
from django.contrib.auth.decorators import login_required
from guardian.shortcuts import get_objects_for_user

@login_required
def student_result_view(request):
    student = request.user  # Get the logged-in faculty member

    # Fetch only sections visible to this student (using object-level permissions if applicable)
    user_sections = get_objects_for_user(student, 'view_section', Section)

    context = {
        **site.each_context(request),  # Includes admin context like available_apps
        'sections': user_sections,
    }

    return render(request, 'results/student_result.html', context)