from django.shortcuts import render

def edit_scores_view(request):
    return render(request, 'assessments/edit_scores.html')

def view_scores_view(request):
    return render(request, 'assessments/view_scores.html')