from django.test import TestCase
from users.models import CustomUser
from django.core.exceptions import ValidationError

class CustomUserModelTestCase(TestCase):
    def setUp(self):
        # Create a CustomUser instance for testing
        self.admin_user = CustomUser.objects.create_user(
            username="admin1",
            first_name="John",
            last_name="Doe",
            email="admin@example.com",
            role="admin",
            password="password123"
        )
        self.student_user = CustomUser.objects.create_user(
            username="student1",
            first_name="Jane",
            email="student@example.com",
            role="student",
            password="password123"
        )

    def test_user_creation(self):
        """Test if CustomUser instances are created properly."""
        self.assertEqual(self.admin_user.username, "admin1")
        self.assertEqual(self.admin_user.role, "admin")
        self.assertEqual(self.student_user.role, "student")

    def test_str_method(self):
        """Test the __str__ method for CustomUser."""
        self.assertEqual(str(self.admin_user), "John Doe")
        self.assertEqual(str(self.student_user), "Jane (student1)")

    def test_role_choices(self):
        """Test that invalid roles raise a ValidationError."""
        invalid_user = CustomUser(
            username="invalid_user",
            first_name="Invalid",
            email="invalid@example.com",
            role="invalid_role",
            password="password123"
        )
        # Check that a ValidationError is raised with specific details
        with self.assertRaises(ValidationError) as context:
            invalid_user.save()  # This calls full_clean() internally

        # Verify the ValidationError details
        self.assertIn('role', context.exception.message_dict)  # Ensure 'role' is the cause
        self.assertEqual(
            context.exception.message_dict['role'],
            ["Value 'invalid_role' is not a valid choice."]
        )