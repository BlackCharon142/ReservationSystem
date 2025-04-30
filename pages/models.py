from django.db import models

class Food(models.Model):
    food_name = models.CharField(max_length=100)