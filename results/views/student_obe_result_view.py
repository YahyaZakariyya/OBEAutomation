from django.shortcuts import render
from django.contrib.admin.sites import site
from django.contrib.auth.decorators import login_required

@login_required
def student_obe_result_view(request):
    """
    Renders the Student OBE result dashboard for the logged-in student.
    """
    context = {
        **site.each_context(request),  # Includes admin context like available_apps
    }

    return render(request, 'results/student_obe_result.html', context)
