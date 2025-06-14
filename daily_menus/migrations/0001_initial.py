# Generated by Django 5.2 on 2025-04-30 13:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('menu_items', '0002_rename_drink_drinks_rename_food_foods_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='DailyMenuItems',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('max_purchasable_quantity', models.PositiveIntegerField(default=1)),
                ('expiration_date', models.DateTimeField()),
                ('normal_date', models.DateTimeField(editable=False)),
                ('drink', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='daily_menus', to='menu_items.drinks')),
                ('food', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='daily_menus', to='menu_items.foods')),
                ('side_dishes', models.ManyToManyField(related_name='daily_menus', to='menu_items.sidedishes')),
            ],
        ),
    ]
