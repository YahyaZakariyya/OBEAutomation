from django.urls import path
from .views import *

urlpatterns = [
    path('sections/', StudentSectionsAPI.as_view(), name='student_sections'),
    path('section/<int:section_id>/clo_attainment/', CLOAttainmentAPI.as_view(), name='clo_attainment'),
    path('faculty/sections/', FacultySectionsList.as_view(), name='faculty-sections'),
    path('faculty/section/<int:section_id>/clo_attainment/', FacultyCLOAttainment.as_view(), name='faculty-clo-attainment'),
    path('student/section/<section_id>/final_result/', StudentFinalResultAPI.as_view(), name='student-final-result'),
    path('faculty/section/<section_id>/final_result/', FacultyFinalResultsAPI.as_view(), name='faculty-final-result'),
]
