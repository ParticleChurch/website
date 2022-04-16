# Generated by Django 4.0.1 on 2022-03-12 08:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('particle_sessions', '0002_particlesession_platform'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='particlesession',
            name='id',
        ),
        migrations.AlterField(
            model_name='particlesession',
            name='session_id',
            field=models.CharField(max_length=32, primary_key=True, serialize=False, unique=True),
        ),
    ]
