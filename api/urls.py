from django.urls import path
from .views import *

urlpatterns = [
    path('sections/', SectionsAPI.as_view(), name='student_sections'),
    path('section/<int:section_id>/clo_attainment/', CLOAttainmentAPI.as_view(), name='clo_attainment'),
    path('faculty/sections/', FacultySectionsList.as_view(), name='faculty-sections'),
    path('faculty/section/<int:section_id>/clo_attainment/', FacultyCLOAttainment.as_view(), name='faculty-clo-attainment'),
    path('student/section/<section_id>/final_result/', StudentResultDetailsAPI.as_view(), name='student-final-result'),
    path('faculty/section/<section_id>/final_result/', FacultyResultDetailsAPI.as_view(), name='faculty-final-result'),
    path('results/', StudentResultsView.as_view(), name='student_results'),
    path('assessment-marks/', MarksAPI.as_view(), name='assessment-marks'),
    path('courses/<int:program_id>/', CoursesByProgram.as_view(), name='get_courses'),
    path('get-course-id/', CourseBySection.as_view(), name='get_course_by_section'),
    path('plos/<int:program_id>/', get_plos_by_program, name='get_plos'),
    path('clos/<int:course_id>/', get_clos_by_course, name='get_clos'),
]
