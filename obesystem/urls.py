from django.urls import path
from . import views

urlpatterns = [
    path('faculty-result-view/', views.faculty_result_view, name='faculty_result_view'),
    path('student-result-view/', views.student_result_view, name='student_result_view'),
]
