# Generated by Django 5.2 on 2025-05-09 09:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_alter_profile_wallet_balance'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='image',
            field=models.ImageField(default='/static/images/default-profile.webp', upload_to='images/profiles/'),
        ),
    ]
