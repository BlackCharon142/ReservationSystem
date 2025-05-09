import io
import jdatetime
from collections import Counter

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from django.db.models import Q

import qrcode
from qrcode.image.svg import SvgPathImage

from reservations.models import Reservation, Status

class Command(BaseCommand):
    help = "Mark past-due reservations as expired (unless already used)."

    def handle(self, *args, **options):
        now = jdatetime.datetime.now()

        # 1) find all codes still “reserved” whose item has expired
        reserved_qs = Reservation.objects.filter(
            status__status='reserved',
            dailymenu__expiration_date__lt=now
        )

        # 2) group by code, count reserved vs canceled vs used
        counts = {}
        for r in reserved_qs:
            code = r.reservation_code
            entry = counts.setdefault(code, {"reserved": 0, "canceled": 0, "used": 0})
            entry["reserved"] += 1

        for r in Reservation.objects.filter(
            reservation_code__in=counts.keys(),
        ):
            code = r.reservation_code
            if r.status.status == 'canceled':
                counts[code]["canceled"] += 1
            elif r.status.status == 'used':
                counts[code]["used"] += 1

        # 3) for each code where reserved > canceled AND used == 0 → expire
        expired_status = Status.objects.get(status='expired')
        to_expire = [
            code for code, cnt in counts.items()
            if cnt["reserved"] > cnt["canceled"] and cnt["used"] == 0
        ]

        if not to_expire:
            self.stdout.write("No reservations to expire.")
            return

        self.stdout.write(f"Expiring {len(to_expire)} codes…")
        for code in to_expire:
            # pick any one of the reserved records to copy the dailymenu & user
            orig = reserved_qs.filter(reservation_code=code).first()
            if not orig:
                continue

            with transaction.atomic():
                Reservation.objects.create(
                    user=orig.user,
                    dailymenu=orig.dailymenu,
                    status=expired_status,
                    reservation_code=code
                )
        self.stdout.write("Done.")