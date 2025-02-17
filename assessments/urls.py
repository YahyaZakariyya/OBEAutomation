from django.urls import path
from .views import edit_scores_view, view_scores_view

urlpatterns = [
    path('edit-scores/', edit_scores_view, name='edit_scores'),
    path('view-scores/', view_scores_view, name='view_scores'),
]