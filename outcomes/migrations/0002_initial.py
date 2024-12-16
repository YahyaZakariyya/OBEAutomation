# Generated by Django 5.0.4 on 2024-12-16 11:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('outcomes', '0001_initial'),
        ('programs', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ploclomapping',
            name='program',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='clo_mappings', to='programs.program'),
        ),
        migrations.AddField(
            model_name='programlearningoutcome',
            name='program',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='program_outcomes', to='programs.program'),
        ),
        migrations.AddField(
            model_name='ploclomapping',
            name='plo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='clo_mappings', to='outcomes.programlearningoutcome'),
        ),
        migrations.AddConstraint(
            model_name='courselearningoutcome',
            constraint=models.UniqueConstraint(fields=('course', 'CLO'), name='unique_clo_per_course'),
        ),
        migrations.AddConstraint(
            model_name='programlearningoutcome',
            constraint=models.UniqueConstraint(fields=('program', 'PLO'), name='unique_plo_per_program'),
        ),
        migrations.AlterUniqueTogether(
            name='ploclomapping',
            unique_together={('program', 'course', 'clo')},
        ),
    ]
