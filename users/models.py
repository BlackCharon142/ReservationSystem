from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.templatetags.static import static
from PIL import Image
from daily_menus.models import MealType
import os

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/profiles/', blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    wallet_balance = models.DecimalField(max_digits=30, decimal_places=0, default=0)
    allowed_meal_type = models.ManyToManyField(MealType, blank=True)
    security_answer_1 = models.CharField(max_length=255, blank=True)
    security_answer_2 = models.CharField(max_length=255, blank=True)
    security_answer_3 = models.CharField(max_length=255, blank=True)
    security_answer_4 = models.CharField(max_length=255, blank=True)
    security_answer_5 = models.CharField(max_length=255, blank=True)

    @property
    def image_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        return static('images/default-profile.webp')

    def __str__(self):
        return f'{self.user.username} Profile'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Only process if an actual image is uploaded
        if self.image and self.image.name and os.path.isfile(self.image.path):
            img = Image.open(self.image.path)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.image.path)

class Guest(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=254, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"{self.firstname} {self.lastname} (ID: {self.guest_id})"

class RecoveryRequest(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="recovery_requests"
    )
    security_answer_1 = models.CharField(max_length=255, editable=False)
    security_answer_2 = models.CharField(max_length=255, editable=False)
    security_answer_3 = models.CharField(max_length=255, editable=False)
    security_answer_4 = models.CharField(max_length=255, editable=False)
    security_answer_5 = models.CharField(max_length=255, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    fulfilled = models.BooleanField(default=False)

    def __str__(self):
        return f"Recovery for {self.user.username} @ {self.created_at:%Y-%m-%d %H:%M}"