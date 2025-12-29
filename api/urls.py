from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

# Import ViewSets
from programs.viewsets import ProgramViewSet
from users.viewsets import UserViewSet
from courses.viewsets import CourseViewSet
from sections.viewsets import SectionViewSet
from assessments.viewsets import (
    AssessmentViewSet,
    AssessmentBreakdownViewSet,
    QuestionViewSet,
    StudentQuestionScoreViewSet
)
from outcomes.viewsets import (
    CLOViewSet,
    PLOViewSet,
    PloCloMappingViewSet
)

# Create router and register ViewSets
router = DefaultRouter()
router.register(r'programs', ProgramViewSet, basename='program')
router.register(r'users', UserViewSet, basename='user')
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'sections', SectionViewSet, basename='section')
router.register(r'assessments', AssessmentViewSet, basename='assessment')
router.register(r'assessment-breakdowns', AssessmentBreakdownViewSet, basename='assessmentbreakdown')
router.register(r'questions', QuestionViewSet, basename='question')
router.register(r'student-scores', StudentQuestionScoreViewSet, basename='studentquestion score')
router.register(r'clos', CLOViewSet, basename='clo')
router.register(r'plos', PLOViewSet, basename='plo')
router.register(r'plo-clo-mappings', PloCloMappingViewSet, basename='ploclomapping')

urlpatterns = [
    # DRF Router URLs
    path('', include(router.urls)),

    # Legacy API endpoints (kept for backward compatibility)
    path('legacy/sections/', SectionsAPI.as_view(), name='select-section'),
    path('legacy/student/section/<section_id>/final_result/', StudentResultDetailsAPI.as_view(), name='student-traditional-result'),
    path('legacy/faculty/section/<section_id>/final_result/', FacultyResultDetailsAPI.as_view(), name='faculty-traditional-result'),
    path('legacy/assessment-marks/', MarksAPI.as_view(), name='assessment-marks'),
    path('legacy/student-score/', StudentScoreAPI.as_view(), name='student-score'),
    path('legacy/courses/<int:program_id>/', CoursesByProgram.as_view(), name='get_courses'),
    path('legacy/get-course-id/', CourseBySection.as_view(), name='get_course_by_section'),
    path('legacy/results/', StudentResultsView.as_view(), name='student_results'),
    path('legacy/clos/<int:course_id>/', get_clos_by_course, name='get_clos'),
    path('legacy/faculty/section/<int:section_id>/clo_result/', FacultyCLOAttainmentAPI.as_view(), name='faculty-clo-result'),
    path('legacy/student/section/<int:section_id>/clo_result/', StudentCLOAttainmentAPI.as_view(), name='student-clo-result'),

    # Dashboard endpoints
    path('dashboards/admin/', admin_dashboard, name='admin-dashboard'),
    path('dashboards/student/', student_dashboard, name='student-dashboard'),
    path('dashboards/faculty/', faculty_dashboard, name='faculty-dashboard'),
]
