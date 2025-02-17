from django.urls import path
from .views import faculty_result_view, student_result_view, faculty_obe_result_view, student_obe_result_view

urlpatterns = [
    path('faculty-result-view/', faculty_result_view, name='faculty_result_view'),
    path('faculty-obe-result-view/', faculty_obe_result_view, name='faculty_obe_result_view'),
    path('student-result-view/', student_result_view, name='student_result_view'),
    path('student-obe-result-view/', student_obe_result_view, name='student_obe_result_view'),
]
