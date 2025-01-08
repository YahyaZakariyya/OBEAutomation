from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.exceptions import ValidationError

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('faculty', 'Faculty Member'),
        ('student', 'Student'),
    )
    role = models.CharField(choices=ROLE_CHOICES, max_length=20, default='student')

    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A group is a collection of permissions.',
        related_name="customuser_set",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="customuser_set",
        related_query_name="user",
    )

    def clean(self):
        super().clean()
        # Validate that the role is within the allowed choices
        valid_roles = [choice[0] for choice in self.ROLE_CHOICES]
        if self.role not in valid_roles:
            raise ValidationError(f"Invalid role: {self.role}. Must be one of {valid_roles}")
        
    def save(self, *args, **kwargs):
        # Call clean before saving to enforce validation
        self.full_clean()  # This will trigger the clean() method
        super().save(*args, **kwargs)

    def __str__(self):
        if self.role == 'student':
            return f"{self.first_name} ({self.username})"
        else:
            return f"{self.first_name} {self.last_name}"