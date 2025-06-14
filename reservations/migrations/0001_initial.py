# Generated by Django 5.2 on 2025-05-08 12:51

import datetime
import django.core.validators
import django.db.models.deletion
import django_jalali.db.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('daily_menus', '0009_dailymenuitem_price'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Status',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reservation_code', models.CharField(max_length=8, unique=True, validators=[django.core.validators.RegexValidator(message='Code must be exactly 8 digits', regex='^\\d{8}$')])),
                ('date_status_updated', django_jalali.db.models.jDateTimeField(default=datetime.datetime(2025, 5, 8, 12, 51, 8, 17683, tzinfo=datetime.timezone.utc))),
                ('dailymenu', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='daily_menus.dailymenuitem')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('status', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='reservations.status')),
            ],
        ),
    ]
