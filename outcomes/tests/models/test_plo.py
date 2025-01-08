from django.test import TestCase
from outcomes.models import ProgramLearningOutcome
from programs.models import Program
from django.core.exceptions import ValidationError


class ProgramLearningOutcomeModelTestCase(TestCase):
    def setUp(self):
        # Create a program for testing
        self.program = Program.objects.create(
            program_title="Computer Science",
            program_abbreviation="CS",
            program_type="UG"
        )

    def test_plo_creation(self):
        """Test creating a valid PLO."""
        plo = ProgramLearningOutcome.objects.create(
            program=self.program,
            PLO=1,
            heading="Critical Thinking",
            description="Develop critical thinking skills.",
            weightage=25
        )
        self.assertEqual(plo.program, self.program)
        self.assertEqual(plo.PLO, 1)
        self.assertEqual(plo.heading, "Critical Thinking")
        self.assertEqual(plo.weightage, 25)

    def test_plo_invalid_weightage(self):
        """Test that weightage beyond valid range raises a ValidationError."""
        plo = ProgramLearningOutcome(
            program=self.program,
            PLO=1,
            heading="Invalid Weightage",
            description="Example PLO with invalid weightage.",
            weightage=110  # Exceeds 100%
        )
        with self.assertRaises(ValidationError):
            plo.full_clean()  # Trigger validation

    def test_unique_plo_per_program(self):
        """Test that the same PLO number cannot be reused in the same program."""
        ProgramLearningOutcome.objects.create(
            program=self.program,
            PLO=1,
            heading="Critical Thinking",
            description="Develop critical thinking skills.",
            weightage=25
        )
        duplicate_plo = ProgramLearningOutcome(
            program=self.program,
            PLO=1,  # Same PLO number
            heading="Duplicate PLO",
            description="Another PLO with the same number.",
            weightage=10
        )
        with self.assertRaises(ValidationError):
            duplicate_plo.full_clean()  # Trigger validation

    def test_plo_weightage_limit(self):
        """Test that total weightage for a program cannot exceed 100%."""
        ProgramLearningOutcome.objects.create(
            program=self.program,
            PLO=1,
            heading="Critical Thinking",
            description="Develop critical thinking skills.",
            weightage=60
        )
        plo2 = ProgramLearningOutcome(
            program=self.program,
            PLO=2,
            heading="Teamwork",
            description="Foster teamwork and collaboration.",
            weightage=50  # This would exceed 100%
        )
        with self.assertRaises(ValidationError):
            plo2.full_clean()  # Trigger custom validation

    def test_cascade_on_program_deletion(self):
        """Test that PLOs are deleted when their related program is deleted."""
        plo = ProgramLearningOutcome.objects.create(
            program=self.program,
            PLO=1,
            heading="Critical Thinking",
            description="Develop critical thinking skills.",
            weightage=25
        )
        self.program.delete()
        self.assertEqual(ProgramLearningOutcome.objects.filter(pk=plo.pk).count(), 0)

    def test_str_method(self):
        """Test the string representation of a PLO."""
        plo = ProgramLearningOutcome.objects.create(
            program=self.program,
            PLO=1,
            heading="Critical Thinking",
            description="Develop critical thinking skills.",
            weightage=25
        )
        self.assertEqual(str(plo), "PLO 1: Critical Thinking")
