# Generated by Django 5.2 on 2025-04-30 19:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_profile_phone_number_profile_security_answer_1_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='recoveryrequest',
            old_name='answer_1',
            new_name='security_answer_1',
        ),
        migrations.RenameField(
            model_name='recoveryrequest',
            old_name='answer_2',
            new_name='security_answer_2',
        ),
        migrations.RenameField(
            model_name='recoveryrequest',
            old_name='answer_3',
            new_name='security_answer_3',
        ),
        migrations.RenameField(
            model_name='recoveryrequest',
            old_name='answer_4',
            new_name='security_answer_4',
        ),
        migrations.RenameField(
            model_name='recoveryrequest',
            old_name='answer_5',
            new_name='security_answer_5',
        ),
    ]
