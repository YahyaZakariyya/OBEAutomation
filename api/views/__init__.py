from .section_api import SectionsAPI
from .student_result_details_api import StudentResultDetailsAPI
from .faculty_result_details_api import FacultyResultDetailsAPI
from .students_edit_score_api import MarksAPI
from .courses import CoursesByProgram, CourseBySection
from .faculty_clo_attainment_api import FacultyCLOAttainmentAPI
from .student_clo_attainment_api import StudentCLOAttainmentAPI
from .outcomes_api import get_plos_by_program, get_clos_by_course
from .students_view_score_api import StudentScoreAPI
from .student_result_view import StudentResultsView
from .admin_dashboard import admin_dashboard
from .student_dashboard import student_dashboard
from .faculty_dashboard import faculty_dashboard
from .user_api import UserListCreateAPI, UserDetailAPI
from .auth_api import UserInfoAPI
from .program_api import ProgramListCreateAPI, ProgramDetailAPI
from .course_api import CourseListCreateAPI, CourseDetailAPI
from .section_crud_api import SectionListCreateAPI, SectionDetailAPI, SectionStudentsAPI
from .assessment_crud_api import AssessmentListCreateAPI, AssessmentDetailAPI
from .question_api import QuestionListCreateAPI, QuestionDetailAPI
from .breakdown_api import BreakdownAPI
from .plo_api import PLOListCreateAPI, PLODetailAPI
from .clo_api import CLOListCreateAPI, CLODetailAPI
from .mapping_api import MappingListCreateAPI, MappingDetailAPI
