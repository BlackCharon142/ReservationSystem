# Generated by Django 5.2 on 2025-04-30 14:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('menu_items', '0005_food_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='food',
            name='image',
            field=models.ImageField(default='images/default-food.png', upload_to='food/'),
        ),
    ]
