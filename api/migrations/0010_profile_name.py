# Generated by Django 5.1.3 on 2024-11-25 05:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_profile_address_profile_phone'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]