from django.urls import path
from .views import *

urlpatterns = [
    path('sections/', SectionsAPI.as_view(), name='select-section'),
    path('student/section/<section_id>/final_result/', StudentResultDetailsAPI.as_view(), name='student-traditional-result'),
    path('faculty/section/<section_id>/final_result/', FacultyResultDetailsAPI.as_view(), name='faculty-traditional-result'),
    path('assessment-marks/', MarksAPI.as_view(), name='assessment-marks'),
    path('student-score/', StudentScoreAPI.as_view(), name='student-score'),
    path('courses/<int:program_id>/', CoursesByProgram.as_view(), name='get_courses'),
    path('get-course-id/', CourseBySection.as_view(), name='get_course_by_section'),
    path('results/', StudentResultsView.as_view(), name='student_results'),
    # path('plos/<int:program_id>/', get_plos_by_program, name='get_plos'),
    path('clos/<int:course_id>/', get_clos_by_course, name='get_clos'),
    path('faculty/section/<int:section_id>/clo_result/', FacultyCLOAttainmentAPI.as_view(), name='faculty-clo-result'),
    path('student/section/<int:section_id>/clo_result/<int:student_id>/', StudentCLOAttainmentAPI.as_view(), name='student-clo-result'),
]
