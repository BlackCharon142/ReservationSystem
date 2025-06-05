from django.contrib import admin
from reservations.models import Reservation, Status

# Register your models here.

admin.site.register(Reservation)
admin.site.register(Status)
