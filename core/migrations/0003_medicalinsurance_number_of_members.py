# Generated by Django 5.0.1 on 2024-06-08 15:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_medicalinsurance_familyinsurance_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='medicalinsurance',
            name='number_of_members',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
