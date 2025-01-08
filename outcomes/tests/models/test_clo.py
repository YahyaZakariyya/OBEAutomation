from django.test import TestCase
from outcomes.models import CourseLearningOutcome
from courses.models import Course
from programs.models import Program
from django.core.exceptions import ValidationError


class CourseLearningOutcomeModelTestCase(TestCase):
    def setUp(self):
        # Create a program and course for testing
        self.program = Program.objects.create(
            program_title="Computer Science",
            program_abbreviation="CS",
            program_type="UG"
        )
        self.course = Course.objects.create(
            course_id="CS101",
            name="Data Structures",
            credit_hours=3
        )
        self.course.programs.add(self.program)  # Link course to program

    def test_clo_creation(self):
        """Test creating a valid CLO."""
        clo = CourseLearningOutcome.objects.create(
            course=self.course,
            CLO=1,
            heading="Understand Arrays",
            description="Learn how to implement and use arrays.",
            weightage=25
        )
        self.assertEqual(clo.course, self.course)
        self.assertEqual(clo.CLO, 1)
        self.assertEqual(clo.heading, "Understand Arrays")
        self.assertEqual(clo.weightage, 25)

    def test_clo_invalid_weightage(self):
        """Test that weightage beyond valid range raises a ValidationError."""
        clo = CourseLearningOutcome(
            course=self.course,
            CLO=1,
            heading="Invalid Weightage",
            description="Example CLO with invalid weightage.",
            weightage=110  # Exceeds 100%
        )
        with self.assertRaises(ValidationError):
            clo.full_clean()  # Trigger validation

    def test_unique_clo_per_course(self):
        """Test that the same CLO number cannot be reused in the same course."""
        CourseLearningOutcome.objects.create(
            course=self.course,
            CLO=1,
            heading="Understand Arrays",
            description="Learn arrays.",
            weightage=25
        )
        duplicate_clo = CourseLearningOutcome(
            course=self.course,
            CLO=1,  # Same CLO number
            heading="Duplicate CLO",
            description="Another CLO with the same number.",
            weightage=10
        )
        with self.assertRaises(ValidationError) as context:
            duplicate_clo.full_clean()  # Trigger validation
        self.assertIn(
            "CLO with this Course and CLO already exists.",
            context.exception.messages
        )

    def test_clo_weightage_limit(self):
        """Test that total weightage for a course cannot exceed 100%."""
        CourseLearningOutcome.objects.create(
            course=self.course,
            CLO=1,
            heading="Understand Arrays",
            description="Learn arrays.",
            weightage=60
        )
        clo2 = CourseLearningOutcome(
            course=self.course,
            CLO=2,
            heading="Understand Linked Lists",
            description="Learn linked lists.",
            weightage=50  # This would exceed 100%
        )
        with self.assertRaises(ValidationError):
            clo2.full_clean()  # Trigger custom validation in the model

    def test_cascade_on_course_deletion(self):
        """Test that CLOs are deleted when their related course is deleted."""
        clo = CourseLearningOutcome.objects.create(
            course=self.course,
            CLO=1,
            heading="Understand Arrays",
            description="Learn arrays.",
            weightage=25
        )
        self.course.delete()
        self.assertEqual(CourseLearningOutcome.objects.filter(pk=clo.pk).count(), 0)

    def test_str_method(self):
        """Test the string representation of a CLO."""
        clo = CourseLearningOutcome.objects.create(
            course=self.course,
            CLO=1,
            heading="Understand Arrays",
            description="Learn arrays.",
            weightage=25
        )
        self.assertEqual(str(clo), "CLO 1: Understand Arrays")
