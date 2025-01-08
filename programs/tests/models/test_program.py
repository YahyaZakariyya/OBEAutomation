from django.test import TestCase
from programs.models import Program
from users.models import CustomUser
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError


class ProgramModelTestCase(TestCase):
    def setUp(self):
        # Create a faculty user to assign as program_incharge
        self.faculty_user = CustomUser.objects.create_user(
            username="faculty1",
            first_name="Alice",
            email="faculty@example.com",
            role="faculty",
            password="password123"
        )

        # Create another faculty user
        self.another_faculty = CustomUser.objects.create_user(
            username="faculty2",
            first_name="Bob",
            email="bob@example.com",
            role="faculty",
            password="password123"
        )

    def test_program_creation(self):
        """Test if a Program instance is created properly with valid data."""
        program = Program.objects.create(
            program_title="Computer Science",
            program_abbreviation="CS",
            program_incharge=self.faculty_user,
            program_type="UG"
        )
        self.assertEqual(program.program_title, "Computer Science")
        self.assertEqual(program.program_abbreviation, "CS")
        self.assertEqual(program.program_incharge, self.faculty_user)
        self.assertEqual(program.program_type, "UG")

    def test_program_unique_abbreviation(self):
        """Test that the program_abbreviation field is unique."""
        Program.objects.create(
            program_title="Computer Science",
            program_abbreviation="CS",
            program_incharge=self.faculty_user,
            program_type="UG"
        )
        with self.assertRaises(IntegrityError):
            Program.objects.create(
                program_title="Data Science",
                program_abbreviation="CS",  # Duplicate abbreviation
                program_incharge=self.another_faculty,
                program_type="UG"
            )

    def test_invalid_program_type(self):
        """Test that an invalid program_type raises a ValidationError."""
        program = Program(
            program_title="Invalid Program",
            program_abbreviation="IP",
            program_incharge=self.faculty_user,
            program_type="INVALID_TYPE"  # Invalid type
        )
        with self.assertRaises(ValidationError):
            program.full_clean()  # Triggers validation

    def test_null_program_incharge(self):
        """Test that a Program can be created with a null program_incharge."""
        program = Program.objects.create(
            program_title="Mathematics",
            program_abbreviation="MATH",
            program_incharge=None,  # No incharge assigned
            program_type="UG"
        )
        self.assertIsNone(program.program_incharge)

    def test_str_method(self):
        """Test the __str__ method for Program."""
        program = Program.objects.create(
            program_title="Physics",
            program_abbreviation="PHY",
            program_incharge=self.faculty_user,
            program_type="UG"
        )
        self.assertEqual(str(program), "PHY")
