# Generated by Django 5.2 on 2025-05-08 19:26

import datetime
import django.core.validators
import django_jalali.db.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0012_alter_reservation_date_status_updated'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reservation',
            name='date_status_updated',
            field=django_jalali.db.models.jDateTimeField(default=datetime.datetime(2025, 5, 8, 22, 56, 43, 931233)),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='reservation_code',
            field=models.CharField(max_length=8, validators=[django.core.validators.RegexValidator(message='Code must be exactly 8 digits', regex='^\\d{8}$')]),
        ),
    ]
