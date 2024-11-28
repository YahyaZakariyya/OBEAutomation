from django.db import models
from .custom_user import CustomUser

class Program(models.Model):
    name = models.CharField(max_length=100)
    hod = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='program_heads', limit_choices_to={'role': 'faculty'})

    def __str__(self):
        return self.name