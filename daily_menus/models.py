from django.db import models
from django.utils import timezone
from menu_items.models import Food, Drink, SideDish
from django_jalali.db import models as jmodels

class DailyMenuItem(models.Model):
    food = models.ForeignKey(Food, on_delete=models.CASCADE, related_name='daily_menus')
    drink = models.ForeignKey(Drink, on_delete=models.CASCADE, related_name='daily_menus')
    side_dishes = models.ManyToManyField(SideDish, related_name='daily_menus')  # Allows multiple selections

    quantity = models.PositiveIntegerField(default=1)  # Quantity of the item
    max_purchasable_quantity = models.PositiveIntegerField(default=1)  # Max quantity allowed for purchase

    image = models.ImageField(upload_to='images/food/', blank=True, null=True)

    objects = jmodels.jManager()
    # Expiration date with Persian calendar picker
    reservation_deadline = jmodels.jDateTimeField(blank=True, null=True)  # DateTime field for deadline
    expiration_date = jmodels.jDateTimeField()  # DateTime field for expiration

    price = models.DecimalField(max_digits=30, decimal_places=0, default=0)

    @property
    def image_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        return self.food.image_url

    def save(self, *args, **kwargs):
        if not self.image and self.food.image:
            self.image = self.food.image
        if not self.reservation_deadline:
            self.reservation_deadline = self.expiration_date
        super().save(*args, **kwargs)

    def __str__(self):
        side_dishes_names = ", ".join([side_dish.name for side_dish in self.side_dishes.all()])
        return "%s & %s - Side Dishes: (%s) - Expiry: (%s)" % (
        self.food.name, self.drink.name, side_dishes_names, self.expiration_date)
        #return f"{self.food.name} & {self.drink.name} - Expire: {self.expiration_date}"

# Note: Remember to install a Persian calendar widget in your forms for expiration_date.
