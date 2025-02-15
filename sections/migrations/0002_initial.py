# Generated by Django 5.0.4 on 2024-12-16 11:41

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('programs', '0002_initial'),
        ('sections', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='section',
            name='faculty',
            field=models.ForeignKey(limit_choices_to={'role': 'faculty'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='taught_sections', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='section',
            name='program',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sections', to='programs.program'),
        ),
        migrations.AddField(
            model_name='section',
            name='students',
            field=models.ManyToManyField(blank=True, limit_choices_to={'role': 'student'}, related_name='enrolled_sections', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddConstraint(
            model_name='section',
            constraint=models.UniqueConstraint(fields=('course', 'program', 'semester', 'section', 'batch', 'year'), name='unique_section_constraint'),
        ),
    ]
