from django.test import TestCase
from courses.models import Course
from programs.models import Program
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError


class CourseModelTestCase(TestCase):
    def setUp(self):
        # Create Programs for testing
        self.program1 = Program.objects.create(
            program_title="Computer Science",
            program_abbreviation="CS",
            program_type="UG"
        )
        self.program2 = Program.objects.create(
            program_title="Artificial Intelligence",
            program_abbreviation="AI",
            program_type="UG"
        )

    def test_course_creation(self):
        """Test that a Course instance can be created with valid data."""
        course = Course.objects.create(
            course_id="CS101",
            name="Data Structures",
            credit_hours=3
        )
        course.programs.add(self.program1, self.program2)  # Add relationships
        self.assertEqual(course.course_id, "CS101")
        self.assertEqual(course.name, "Data Structures")
        self.assertEqual(course.credit_hours, 3)
        self.assertQuerysetEqual(
            course.programs.all(),
            [self.program1, self.program2],
            transform=lambda x: x,  # Compare actual objects
            ordered=False
        )

    def test_course_invalid_credit_hours(self):
        """Test that credit_hours outside valid range raises a ValidationError."""
        course = Course(course_id="CS102", name="Algorithms", credit_hours=5)
        with self.assertRaises(ValidationError):
            course.full_clean()  # Trigger field validation

    def test_course_unique_constraints(self):
        """Test that duplicate course_id, name, and credit_hours raises an IntegrityError."""
        Course.objects.create(
            course_id="CS103",
            name="Operating Systems",
            credit_hours=3
        )
        with self.assertRaises(IntegrityError):
            Course.objects.create(
                course_id="CS103",  # Same course_id
                name="Operating Systems",  # Same name
                credit_hours=3  # Same credit_hours
            )

    def test_str_method(self):
        """Test the __str__ method of the Course model."""
        course = Course.objects.create(
            course_id="CS104",
            name="Computer Networks",
            credit_hours=3
        )
        self.assertEqual(str(course), "Computer Networks (CS104)")