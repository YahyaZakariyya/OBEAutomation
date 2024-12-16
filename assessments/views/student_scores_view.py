from django.shortcuts import render

def edit_scores_view(request):
    # This view just returns the HTML template
    return render(request, 'assessments/edit_scores.html')