from django.test import TestCase
from outcomes.models import PloCloMapping, ProgramLearningOutcome, CourseLearningOutcome
from programs.models import Program
from courses.models import Course
from django.core.exceptions import ValidationError


class PloCloMappingModelTestCase(TestCase):
    def setUp(self):
        # Create a program and course
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

        # Create PLO and CLO
        self.plo = ProgramLearningOutcome.objects.create(
            program=self.program,
            PLO=1,
            heading="Critical Thinking",
            description="Develop critical thinking skills.",
            weightage=50
        )
        self.clo = CourseLearningOutcome.objects.create(
            course=self.course,
            CLO=1,
            heading="Understand Arrays",
            description="Learn arrays.",
            weightage=25
        )

    def test_mapping_creation(self):
        """Test creating a valid mapping."""
        mapping = PloCloMapping.objects.create(
            program=self.program,
            course=self.course,
            plo=self.plo,
            clo=self.clo,
            weightage=20
        )
        self.assertEqual(mapping.program, self.program)
        self.assertEqual(mapping.course, self.course)
        self.assertEqual(mapping.plo, self.plo)
        self.assertEqual(mapping.clo, self.clo)
        self.assertEqual(mapping.weightage, 20)

    def test_unique_clo_per_course(self):
        """Test that a CLO can only map to one PLO in the same course."""
        PloCloMapping.objects.create(
            program=self.program,
            course=self.course,
            plo=self.plo,
            clo=self.clo,
            weightage=20
        )
        duplicate_mapping = PloCloMapping(
            program=self.program,
            course=self.course,
            plo=self.plo,
            clo=self.clo,
            weightage=10
        )
        with self.assertRaises(ValidationError):
            duplicate_mapping.full_clean()  # Trigger validation

    def test_weightage_validation(self):
        """Test that the total weightage for a PLO in a course does not exceed 100%."""
        PloCloMapping.objects.create(
            program=self.program,
            course=self.course,
            plo=self.plo,
            clo=self.clo,
            weightage=90
        )
        new_mapping = PloCloMapping(
            program=self.program,
            course=self.course,
            plo=self.plo,
            clo=self.clo,
            weightage=20  # This would exceed 100%
        )
        with self.assertRaises(ValidationError):
            new_mapping.full_clean()  # Trigger validation

    def test_cascade_on_deletion(self):
        """Test that mappings are deleted when related objects are deleted."""
        mapping = PloCloMapping.objects.create(
            program=self.program,
            course=self.course,
            plo=self.plo,
            clo=self.clo,
            weightage=20
        )
        self.course.delete()  # Deleting the course should delete the mapping
        self.assertEqual(PloCloMapping.objects.filter(pk=mapping.pk).count(), 0)

    def test_str_method(self):
        """Test the string representation of a mapping."""
        mapping = PloCloMapping.objects.create(
            program=self.program,
            course=self.course,
            plo=self.plo,
            clo=self.clo,
            weightage=20
        )
        expected_str = f"{self.program} - {self.course} - {self.clo} maps to {self.plo} (Weightage: 20.0%)"
        self.assertEqual(str(mapping), expected_str)
