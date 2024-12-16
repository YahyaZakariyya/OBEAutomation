# Generated by Django 5.0.4 on 2024-12-16 11:41

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('programs', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='program',
            name='hod',
            field=models.ForeignKey(limit_choices_to={'role': 'faculty'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='program_heads', to=settings.AUTH_USER_MODEL),
        ),
    ]
