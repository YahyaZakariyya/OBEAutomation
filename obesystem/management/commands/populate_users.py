import os
import django
import random
from django.contrib.auth.models import Group
from faker import Faker

# Set up Django environment
os.environ['DJANGO_SETTINGS_MODULE'] = 'OBEAutomation.settings'  # Update with your actual settings module path
django.setup()

from obesystem.models import CustomUser  # Replace 'obesystem' with your actual app name

# Initialize Faker
fake = Faker()

# Ensure "Students" group exists and fetch it
try:
    students_group = Group.objects.get(name="Students")
except Group.DoesNotExist:
    print("The 'Students' group does not exist. Please create it first in the Django admin.")
    exit()

# Generate 50 users
for _ in range(50):
    # Generate a random 5-digit username
    username = f"{random.randint(10000, 99999)}"
    
    # Define other fields based on the username
    password = f"RSCI@{username}"
    email = f"{username}@students.riphah.edu.pk"
    first_name = fake.first_name()
    last_name = fake.last_name()
    
    # Create the user and set the password
    user = CustomUser(
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
        role='student',
        is_active=True,
        is_staff=True
    )
    user.set_password(password)  # Automatically hashes the password
    user.save()  # Save the user to the database
    
    # Add the user to the "Students" group
    user.groups.add(students_group)

print("50 users created successfully.")
