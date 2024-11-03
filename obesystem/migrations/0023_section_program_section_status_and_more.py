# Generated by Django 5.0.4 on 2024-11-03 11:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('obesystem', '0022_alter_course_unique_together_course_programs_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='section',
            name='program',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sections', to='obesystem.program'),
        ),
        migrations.AddField(
            model_name='section',
            name='status',
            field=models.CharField(choices=[('in_progress', 'In Progress'), ('complete', 'Complete')], default='in_progress', max_length=12),
        ),
        migrations.AddConstraint(
            model_name='section',
            constraint=models.UniqueConstraint(fields=('course', 'program', 'semester', 'section', 'batch', 'year'), name='unique_section_constraint'),
        ),
    ]
