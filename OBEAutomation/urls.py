from django.contrib import admin
from django.urls import path, include
# from obesystem.views.reporting import student_clo_performance_view, faculty_clo_dashboard, faculty_result_view


urlpatterns = [
    path('', admin.site.urls),
    path('api/', include('api.urls')),
    path('assessments/', include('assessments.urls')),
    path('results/', include('results.urls')),
]
