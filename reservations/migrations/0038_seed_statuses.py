# Generated by Django 5.2 on 2025-06-06 15:18

from django.db import migrations


def create_statuses(apps, schema_editor):
    Status = apps.get_model("reservations", "Status")
    STATUS_CHOICES = [
        ("reserved", "رزرو شده"),
        ("used", "استفاده شده"),
        ("canceled", "کنسل شده"),
        ("expired", "منقضی شده"),
    ]
    for status, title in STATUS_CHOICES:
        Status.objects.get_or_create(
            status=status,
            defaults={"title": title, "is_visible": True}
        )

class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0037_alter_reservation_date_status_updated'),
    ]


    operations = [
        migrations.RunPython(create_statuses),
    ]
