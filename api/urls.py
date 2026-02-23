from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import *

urlpatterns = [
    # Auth endpoints
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/me/', UserInfoAPI.as_view(), name='user-info'),

    # Users CRUD
    path('users/', UserListCreateAPI.as_view(), name='user-list-create'),
    path('users/<int:pk>/', UserDetailAPI.as_view(), name='user-detail'),

    # Programs CRUD
    path('programs/', ProgramListCreateAPI.as_view(), name='program-list-create'),
    path('programs/<int:pk>/', ProgramDetailAPI.as_view(), name='program-detail'),

    # Courses CRUD
    path('courses/', CourseListCreateAPI.as_view(), name='course-list-create'),
    path('courses/<int:pk>/', CourseDetailAPI.as_view(), name='course-detail'),

    # Sections CRUD
    path('sections/', SectionListCreateAPI.as_view(), name='section-list-create'),
    path('sections/<int:pk>/', SectionDetailAPI.as_view(), name='section-detail'),
    path('sections/<int:pk>/students/', SectionStudentsAPI.as_view(), name='section-students'),
    path('sections/<int:section_id>/breakdown/', BreakdownAPI.as_view(), name='section-breakdown'),

    # Assessments CRUD
    path('assessments/', AssessmentListCreateAPI.as_view(), name='assessment-list-create'),
    path('assessments/<int:pk>/', AssessmentDetailAPI.as_view(), name='assessment-detail'),
    path('assessments/<int:assessment_id>/questions/', QuestionListCreateAPI.as_view(), name='question-list-create'),

    # Questions CRUD
    path('questions/<int:pk>/', QuestionDetailAPI.as_view(), name='question-detail'),

    # PLOs CRUD
    path('plos/', PLOListCreateAPI.as_view(), name='plo-list-create'),
    path('plos/<int:pk>/', PLODetailAPI.as_view(), name='plo-detail'),

    # CLOs CRUD
    path('clos/', CLOListCreateAPI.as_view(), name='clo-list-create'),
    path('clos/<int:pk>/', CLODetailAPI.as_view(), name='clo-detail'),

    # PLO-CLO Mappings
    path('plo-clo-mappings/', MappingListCreateAPI.as_view(), name='mapping-list-create'),
    path('plo-clo-mappings/<int:pk>/', MappingDetailAPI.as_view(), name='mapping-detail'),

    # Legacy endpoints (existing)
    path('legacy/sections/', SectionsAPI.as_view(), name='select-section'),
    path('student/section/<section_id>/final_result/', StudentResultDetailsAPI.as_view(), name='student-traditional-result'),
    path('faculty/section/<section_id>/final_result/', FacultyResultDetailsAPI.as_view(), name='faculty-traditional-result'),
    path('assessment-marks/', MarksAPI.as_view(), name='assessment-marks'),
    path('student-score/', StudentScoreAPI.as_view(), name='student-score'),
    path('courses-by-program/<int:program_id>/', CoursesByProgram.as_view(), name='get_courses'),
    path('get-course-id/', CourseBySection.as_view(), name='get_course_by_section'),
    path('results/', StudentResultsView.as_view(), name='student_results'),
    path('clos-by-course/<int:course_id>/', get_clos_by_course, name='get_clos'),
    path('faculty/section/<int:section_id>/clo_result/', FacultyCLOAttainmentAPI.as_view(), name='faculty-clo-result'),
    path('student/section/<int:section_id>/clo_result/', StudentCLOAttainmentAPI.as_view(), name='student-clo-result'),
    path('admin_dashboard/', admin_dashboard, name='admin-dashboard'),
    path('student_dashboard/', student_dashboard, name='student-dashboard'),
    path('faculty_dashboard/', faculty_dashboard, name='faculty-dashboard'),
]
