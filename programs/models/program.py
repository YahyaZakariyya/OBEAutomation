from django.db import models
from users.models import CustomUser

class Program(models.Model):
    PROGRAM_TYPES = [
        ('UG', 'Undergraduate'),
        ('GR', 'Graduate'),
        ('PG', 'Postgraduate'),
    ]
    program_title = models.CharField(max_length=100)
    program_abbreviation = models.CharField(max_length=10, unique=True)
    program_incharge = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='program_heads', limit_choices_to={'role': 'faculty'})
    program_type = models.CharField(max_length=2, choices=PROGRAM_TYPES)

    def __str__(self):
        return self.program_abbreviation