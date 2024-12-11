from django.urls import path
from .views import StudentSectionsAPI, CLOAttainmentAPI

urlpatterns = [
    path('sections/', StudentSectionsAPI.as_view(), name='student_sections'),
    path('section/<int:section_id>/clo_attainment/', CLOAttainmentAPI.as_view(), name='clo_attainment'),
]
