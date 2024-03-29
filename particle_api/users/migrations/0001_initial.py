# Generated by Django 4.0.1 on 2022-01-30 03:37

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('user_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('time_registered', models.DateTimeField(auto_now_add=True)),
                ('email', models.CharField(max_length=128, unique=True)),
                ('password_hash', models.CharField(max_length=128)),
                ('is_subscribed', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['user_id'],
            },
        ),
    ]
