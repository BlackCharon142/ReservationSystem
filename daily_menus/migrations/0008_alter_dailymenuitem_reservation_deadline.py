# Generated by Django 5.2 on 2025-05-07 14:15

import django_jalali.db.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('daily_menus', '0007_dailymenuitem_reservation_deadline'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dailymenuitem',
            name='reservation_deadline',
            field=django_jalali.db.models.jDateTimeField(blank=True, null=True),
        ),
    ]
