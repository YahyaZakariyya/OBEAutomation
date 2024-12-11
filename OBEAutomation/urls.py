from django.contrib import admin
from django.urls import path, include
from obesystem.views.api import CLOPerformanceAPI, PLOPerformanceAPI, MarksAPI, edit_scores_view, FacultyCLOAnalysisAPI
from obesystem.views.reporting import student_clo_performance_view, faculty_clo_dashboard


urlpatterns = [
    path('student-clo-performance/', student_clo_performance_view, name='student-clo-performance'),
    path('faculty-clo-dashboard/', faculty_clo_dashboard, name='faculty_clo_dashboard'),
    path('api/faculty-clo-analysis/', FacultyCLOAnalysisAPI.as_view(), name='faculty_clo_analysis_api'),
    path('api/assessment-marks/', MarksAPI.as_view(), name='assessment-marks'),
    path("api/clo-performance/", CLOPerformanceAPI.as_view(), name="clo-performance-api"),
    path("api/plo-performance/", PLOPerformanceAPI.as_view(), name="plo-performance-api"),
    path('edit-scores/', edit_scores_view, name='edit-scores'),
    path('', admin.site.urls),

]
