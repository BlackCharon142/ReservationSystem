# Generated by Django 5.2 on 2025-05-15 13:46

import datetime
import django.db.models.deletion
import django_jalali.db.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0020_alter_reservation_date_status_updated'),
        ('users', '0008_guest'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservation',
            name='guest',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.guest'),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='date_status_updated',
            field=django_jalali.db.models.jDateTimeField(default=datetime.datetime(2025, 5, 15, 17, 16, 6, 805158)),
        ),
    ]
