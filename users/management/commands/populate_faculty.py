import os
import django
import random
from faker import Faker

# Set up Django environment
os.environ['DJANGO_SETTINGS_MODULE'] = 'OBEAutomation.settings'  # Update with your actual settings module path
django.setup()

from users.models import CustomUser

# Initialize Faker
fake = Faker()

# Generate 50 users
for _ in range(150):
    # Generate a random 5-digit username
    username = f"f{random.randint(1000, 2000)}"
    
    # Define other fields based on the username
    password = f"RSCI@admin"
    first_name = fake.first_name()
    last_name = fake.last_name()
    email = f"{first_name}.{last_name}@riphah.edu.pk"
    
    # Create the user and set the password
    user = CustomUser(
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
        role='faculty',
        is_active=True,
        is_staff=True
    )
    user.set_password(password)  # Automatically hashes the password
    user.save()  # Save the user to the database

print("15 faculty members created successfully.")
