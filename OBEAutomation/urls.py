from django.contrib import admin
from django.urls import path, re_path
from obesystem.views import MarksAPI, edit_scores_view

urlpatterns = [
    path('api/assessment-marks/', MarksAPI.as_view(), name='assessment-marks'),
    path('edit-scores/', edit_scores_view, name='edit-scores'),
    path('', admin.site.urls),
]
