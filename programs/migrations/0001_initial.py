# Generated by Django 5.0.4 on 2024-12-16 11:41

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Program',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('program_type', models.CharField(choices=[('UG', 'Undergraduate'), ('GR', 'Graduate'), ('PG', 'Postgraduate')], max_length=2)),
            ],
        ),
    ]
