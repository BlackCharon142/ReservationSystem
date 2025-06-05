from django.db import models
from daily_menus.models import DailyMenuItem
from django.contrib.auth.models import User
from users.models import Guest
from django_jalali.db import models as jmodels
import jdatetime
from django.utils import timezone
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

class Status(models.Model):
    title = models.CharField(max_length=100)
    STATUS_CHOICES = [
        ('reserved', 'Reserved'),
        ('used', 'Used'),
        ('canceled', 'Canceled'),
        ('expired', 'Expired'),
    ]
    status = models.CharField(max_length=10, unique=True, choices=STATUS_CHOICES)
    is_visible = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} [{self.status}] {'(Visible)' if self.is_visible else ''}"

class Reservation(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    guest = models.ForeignKey(Guest, null=True, on_delete=models.SET_NULL)
    dailymenu = models.ForeignKey(DailyMenuItem, null=True, on_delete=models.SET_NULL)
    status = models.ForeignKey(Status, null=True, on_delete=models.SET_NULL)

    # Validator to ensure exactly 8 digits
    reservation_code = models.CharField(
        max_length=8,
        validators=[RegexValidator(regex=r'^\d{8}$', message='Code must be exactly 8 digits')]
    )

    objects = jmodels.jManager()
    date_status_updated = jmodels.jDateTimeField(default=jdatetime.datetime.now())

    def clean(self):
        if self.user is None or self.dailymenu is None or self.status is None:
            raise ValidationError('Exactly one of user, dailymenu, or status must be set.')

    def __str__(self):
        if self.guest :
            return f"[ Code: {self.reservation_code} ] Guest: '{self.guest.first_name} {self.guest.last_name}' - Status: '{self.status.title}'"
        else:
            return f"[ Code: {self.reservation_code} ] User: '{self.user.first_name} {self.user.last_name}' - Status: '{self.status.title}'"
