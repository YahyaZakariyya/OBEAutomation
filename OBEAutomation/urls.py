from django.contrib import admin
from django.urls import path, include
from users.urls import urlpatterns as user_urls
# from obesystem.views.reporting import student_clo_performance_view, faculty_clo_dashboard, faculty_result_view


urlpatterns = [
    path('api/', include('api.urls')),
    path('assessments/', include('assessments.urls')),
    path('results/', include('results.urls')),
    path('users/', include(user_urls)),  # Include user URLs for login
    path('', admin.site.urls),
]
