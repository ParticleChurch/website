# Generated by Django 4.0.1 on 2022-02-06 20:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_remove_user_is_subscribed_user_subscription_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='time_subscription_form_succeeded',
            field=models.DateTimeField(default=None, null=True),
        ),
    ]