# Generated by Django 5.2.3 on 2025-07-10 17:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_notification'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='followers',
        ),
    ]
