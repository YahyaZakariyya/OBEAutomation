import sys
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from programs.models.program import Program

User = get_user_model()

class Command(BaseCommand):
    help = 'Seed the database with initial demonstration data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database with initial data for demonstrations...')
        
        # 1. Create Users
        self.stdout.write('Creating users...')
        admin_user = User.objects.filter(username='admin').first()
        if not admin_user:
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123',
                role='admin',
                first_name='System',
                last_name='Admin'
            )
            
        faculty_user = User.objects.filter(username='faculty_demo').first()
        if not faculty_user:
            faculty_user = User.objects.create_user(
                username='faculty_demo',
                email='faculty@example.com',
                password='faculty123',
                role='faculty',
                first_name='Demo',
                last_name='Faculty'
            )
            
        student_user = User.objects.filter(username='student_demo').first()
        if not student_user:
            student_user = User.objects.create_user(
                username='student_demo',
                email='student@example.com',
                password='student123',
                role='student',
                first_name='Demo',
                last_name='Student'
            )

        # 2. Create Programs
        self.stdout.write('Creating programs...')
        program1, created = Program.objects.get_or_create(
            program_abbreviation='BSCS',
            defaults={
                'program_title': 'Bachelor of Science in Computer Science',
                'program_type': 'UG',
                'program_incharge': faculty_user
            }
        )
        
        self.stdout.write(self.style.SUCCESS('\nSuccessfully seeded database with demonstration data!'))
        self.stdout.write(self.style.WARNING('You can login with:'))
        self.stdout.write(self.style.WARNING(' - Admin: admin / admin123'))
        self.stdout.write(self.style.WARNING(' - Faculty: faculty_demo / faculty123'))
        self.stdout.write(self.style.WARNING(' - Student: student_demo / student123'))
