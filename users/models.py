from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from PIL import Image

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='images/default-profile.webp', upload_to='images/profiles/')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    security_answer_1 = models.CharField(max_length=255, blank=True)
    security_answer_2 = models.CharField(max_length=255, blank=True)
    security_answer_3 = models.CharField(max_length=255, blank=True)
    security_answer_4 = models.CharField(max_length=255, blank=True)
    security_answer_5 = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f'{self.user.username} Profile'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        img = Image.open(self.image.path)
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)


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