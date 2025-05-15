from django.contrib import admin
import django_jalali.admin as jadmin
from daily_menus.models import DailyMenuItem, MealType

# Register your models here.

admin.site.register(DailyMenuItem)
admin.site.register(MealType)