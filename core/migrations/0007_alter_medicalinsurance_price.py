# Generated by Django 5.0.1 on 2024-06-18 15:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_alter_medicalinsurance_insurance_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='medicalinsurance',
            name='price',
            field=models.DecimalField(decimal_places=2, editable=False, max_digits=10),
        ),
    ]