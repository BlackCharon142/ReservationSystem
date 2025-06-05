from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.db.models import Q, Count, Case, When, IntegerField, F, Exists, OuterRef
from collections import Counter

from django.contrib.auth import login, authenticate
from pages.forms import LoginForm, RecoveryForm

from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required, user_passes_test

from django.utils import timezone
from django.utils.translation import gettext as _
import jdatetime

from django.http import JsonResponse, HttpResponse, HttpResponseNotAllowed
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse

import hashlib, random

from users.models import Profile, RecoveryRequest
from daily_menus.models import DailyMenuItem
from menu_items.models import Food, Drink, SideDish
from reservations.models import Reservation, Status

from django.contrib.auth import logout
from django.shortcuts import redirect

import io
import qrcode
from qrcode.image.svg import SvgPathImage


class LoginViewPage(LoginView):
    template_name = "index.html"
    form_class = LoginForm

    def get_success_url(self):
        user = self.request.user
        if user.is_superuser or user.is_staff:
            return "/admin/"  # Replace with your desired URL
        else:
            return "/dashboard/"


@login_required
def logout(request):

    logout(request)
    return redirect("/")


def user_password_recovery(request):
    if request.method == "POST":
        form = RecoveryForm(request.POST)
        if form.is_valid():
            # Pull out the five answers
            answers = {
                f"security_answer_{i}": form.cleaned_data[f"answer_{i}"]
                for i in range(1, 6)
            }

            # Find any profiles whose answers all match exactly
            matches = Profile.objects.filter(**answers)

            # Enqueue a RecoveryRequest for every matched user
            for profile in matches:
                RecoveryRequest.objects.create(user=profile.user, **answers)

            # Always show the same generic message, whether or not we found a match
            messages.success(
                request,
                "Thank you. If your answers match one of our records, an administrator will contact you shortly.",
            )
            return render(
                request,
                template_name="user-password-recovery.html",
                context={
                    "form": form,
                    "notification": True,
                    "notification_status": True,
                    "notification_message": "با موفقیت ثبت شد!",
                },
            )
    else:
        form = RecoveryForm()

    return render(
        request, template_name="user-password-recovery.html", context={"form": form}
    )


@login_required
def dashboard(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    # 2) grab ALL reservations for today’s date (by expiration_date)
    today_qs = Reservation.objects.filter(
        user=request.user, dailymenu__expiration_date__date=jdatetime.date.today()
    )

    # 3) split into reserved vs canceled
    reserved_qs = today_qs.filter(status__status="reserved")
    canceled_qs = today_qs.filter(status__status="canceled")

    # 4) count net per code
    reserved_counts = Counter(reserved_qs.values_list("reservation_code", flat=True))
    canceled_counts = Counter(canceled_qs.values_list("reservation_code", flat=True))

    # 5) keep only codes with net>0
    active_codes = [
        code
        for code, cnt in reserved_counts.items()
        if cnt > canceled_counts.get(code, 0)
    ]

    # 5) For each active code, grab its latest record from the full today_qs
    active_today = []
    for code in active_codes:
        rec = (
            today_qs.filter(reservation_code=code)
            .order_by("-date_status_updated")
            .first()
        )
        if rec:
            active_today.append(rec)

    # 7) generate inline SVG QR for each
    for res in active_today:
        qr = qrcode.QRCode(box_size=4, border=1)
        qr.add_data(res.reservation_code)
        qr.make(fit=True)
        img = qr.make_image(image_factory=SvgPathImage)

        buf = io.BytesIO()
        img.save(buf)
        res.qr_svg = buf.getvalue().decode("utf-8")

    return render(
        request,
        "dashboard.html",
        {
            "profile": profile,
            "today_reservations": active_today,
        },
    )


@login_required
def ajax_wallet_balance(request):
    profile = request.user.profile
    # return integer or string formatted as you like
    return JsonResponse(
        {"balance": profile.wallet_balance, "formatted": f"{profile.wallet_balance:,}"}
    )


@login_required
def reserve(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    currentDate = jdatetime.datetime.now()

    today_menu = DailyMenuItem.objects.filter(
        expiration_date__date=currentDate.date(),
        meal_type__in=request.user.profile.allowed_meal_type.all(),
    )

    # Annotate each item with net reserved count for this user & this item & this date:
    #   #reserves – #cancels
    reservations = (
        Reservation.objects.filter(
            user=request.user,
            dailymenu__in=today_menu,
            dailymenu__expiration_date__date=currentDate.date(),
        )
        .values("dailymenu")
        .annotate(
            net=Count(
                Case(
                    When(status__status="reserved", then=1), output_field=IntegerField()
                )
            )
            - Count(
                Case(
                    When(status__status="canceled", then=1), output_field=IntegerField()
                )
            )
        )
    )
    # Build a lookup: { menu_id: net_count, ... }
    reserved_map = {r["dailymenu"]: r["net"] for r in reservations}

    # Now inject max_purchasable_quantity = 0 if past deadline, and reserve_count
    for item in today_menu:
        if item.reservation_deadline <= timezone.make_aware(jdatetime.datetime.now()):
            item.max_purchasable_quantity = 0
        item.reserved_count = reserved_map.get(item.id, 0)

    return render(
        request,
        "reserve.html",
        {
            "profile": profile,
            "todayMenu": today_menu,
            "currentDate": currentDate.timestamp(),
        },
    )


@login_required
@require_GET
def get_meals_by_timestamp(request):
    ts = request.GET.get("timestamp")
    if not ts:
        return JsonResponse({"error": "Missing timestamp"}, status=400)

    try:
        ts = int(float(ts))
    except ValueError:
        return JsonResponse({"error": "Invalid timestamp format"}, status=400)

    # build the date to filter on
    dt = jdatetime.datetime.fromtimestamp(ts)
    date = dt.date()

    # fetch the day's menu
    meals = DailyMenuItem.objects.filter(
        expiration_date__date=date,
        meal_type__in=request.user.profile.allowed_meal_type.all(),
    )
    print(request.user.profile.allowed_meal_type.all())

    # compute net reserved vs canceled for this user & date
    reservations = (
        Reservation.objects.filter(
            user=request.user,
            dailymenu__in=meals,
            dailymenu__expiration_date__date=date,
        )
        .values("dailymenu")
        .annotate(
            net=Count(
                Case(When(status__status="reserved", then=1)),
                output_field=IntegerField(),
            )
            - Count(
                Case(When(status__status="canceled", then=1)),
                output_field=IntegerField(),
            )
        )
    )
    reserved_map = {r["dailymenu"]: r["net"] for r in reservations}

    # chosen “now” for deadline checks
    now_aware = timezone.make_aware(
        jdatetime.datetime.now().togregorian(), timezone.get_current_timezone()
    )

    meal_data = []
    for item in meals:
        # enforce deadline
        max_q = (
            item.max_purchasable_quantity
            if item.reservation_deadline >= now_aware
            else 0
        )
        # how many already reserved
        reserved_count = reserved_map.get(item.id, 0)

        meal_data.append(
            {
                "id": item.id,
                "name": item.food.name,
                "description": "، ".join(str(s) for s in item.side_dishes.all()),
                "type": item.meal_type.title,
                "price": item.price,
                "image_url": item.image_url,
                "max_qty": max_q,
                "reserved_count": reserved_count,
            }
        )

    return JsonResponse({"meals": meal_data})


@login_required
@require_POST
def ajax_reserve(request):
    user = request.user
    menu_id = request.POST.get("menu_id")
    try:
        menu_item = DailyMenuItem.objects.select_for_update().get(pk=int(menu_id))
    except (ValueError, DailyMenuItem.DoesNotExist):
        return JsonResponse({"error": "Invalid menu item."}, status=400)

    # check stock
    if menu_item.quantity < 1:
        return JsonResponse({"error": "Out of stock."}, status=400)

    # check wallet
    if user.profile.wallet_balance < menu_item.price:
        return JsonResponse({"error": "Insufficient balance."}, status=400)

    today = menu_item.expiration_date.date()  # same date you use elsewhere

    qs = Reservation.objects.filter(
        user=user,
        dailymenu=menu_item,
        dailymenu__expiration_date__date=today,
    ).aggregate(
        reserved=Count(
            Case(When(status__status="reserved", then=1)), output_field=IntegerField()
        ),
        canceled=Count(
            Case(When(status__status="canceled", then=1)), output_field=IntegerField()
        ),
    )
    net = (qs["reserved"] or 0) - (qs["canceled"] or 0)
    if net > menu_item.max_purchasable_quantity:
        return JsonResponse(
            {
                "error": f"You may only reserve up to {menu_item.max_purchasable_quantity} of this item today."
            },
            status=400,
        )

    reserved_status = Status.objects.get(status="reserved")

    # generate per-user-item-day code
    def make_code():
        raw = (
            f"{user.id}-{menu_item.id}-"
            f"{menu_item.expiration_date.timestamp()}-"
            f"{random.random()}"
        )
        num = int(hashlib.sha256(raw.encode()).hexdigest(), 16) % 10**8
        return f"{num:08d}"

    with transaction.atomic():
        # lock menu_item row
        menu_item.quantity -= 1
        menu_item.save()

        # lock user profile
        profile = user.profile
        profile.wallet_balance -= menu_item.price
        profile.save()

        # ensure uniqueness
        for _ in range(5):
            code = make_code()
            if not Reservation.objects.filter(reservation_code=code).exists():
                break
        else:
            return JsonResponse({"error": "Try again later."}, status=500)

        Reservation.objects.create(
            user=user,
            dailymenu=menu_item,
            status=reserved_status,
            reservation_code=code,
        )

    return JsonResponse({"success": True, "new_qty": menu_item.quantity, "code": code})


@login_required
@require_POST
def ajax_cancel(request):
    user = request.user
    menu_id = request.POST.get("menu_id")
    try:
        menu_item = DailyMenuItem.objects.select_for_update().get(pk=int(menu_id))
    except (ValueError, DailyMenuItem.DoesNotExist):
        return JsonResponse({"error": "Invalid menu item."}, status=400)

    today = menu_item.expiration_date.date()  # same date you use elsewhere

    qs = Reservation.objects.filter(
        user=user,
        dailymenu=menu_item,
        dailymenu__expiration_date__date=today,
    ).aggregate(
        reserved=Count(
            Case(When(status__status="reserved", then=1)), output_field=IntegerField()
        ),
        canceled=Count(
            Case(When(status__status="canceled", then=1)), output_field=IntegerField()
        ),
    )
    net = (qs["reserved"] or 0) - (qs["canceled"] or 0)
    if net < 0:
        return JsonResponse(
            {"error": f"you cant cancel what you havent bought."}, status=400
        )

    # 1) build counters of reserved vs. canceled codes for this user & menu
    reserved_qs = Reservation.objects.filter(
        user=user, dailymenu=menu_item, status__status="reserved"
    ).order_by("date_status_updated")
    canceled_qs = Reservation.objects.filter(
        user=user, dailymenu=menu_item, status__status="canceled"
    )

    reserved_codes = [r.reservation_code for r in reserved_qs]
    canceled_codes = [r.reservation_code for r in canceled_qs]

    res_count = Counter(reserved_codes)
    can_count = Counter(canceled_codes)

    # 2) pick the most recent code whose net > 0
    #    (iterate reserved_qs in reverse chronological order)
    code_to_cancel = None
    for r in reversed(reserved_qs):
        code = r.reservation_code
        if res_count[code] > can_count.get(code, 0):
            code_to_cancel = code
            break

    if not code_to_cancel:
        return JsonResponse({"error": "No active reservation to cancel."}, status=400)

    canceled_status = Status.objects.get(status="canceled")

    # 3) perform the cancel: restore stock & wallet, then record the cancel
    with transaction.atomic():
        menu_item.quantity += 1
        menu_item.save()

        profile = user.profile
        profile.wallet_balance += menu_item.price
        profile.save()

        Reservation.objects.create(
            user=user,
            dailymenu=menu_item,
            status=canceled_status,
            reservation_code=code_to_cancel,
        )

    return JsonResponse(
        {"success": True, "new_qty": menu_item.quantity, "code": code_to_cancel}
    )


@login_required
def reserved(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    future_qs = Reservation.objects.filter(
        user=request.user,
        dailymenu__expiration_date__gt=jdatetime.datetime.now().date(),
    )

    # 3) Split into reserved vs canceled
    reserved_qs = future_qs.filter(status__status="reserved")
    canceled_qs = future_qs.filter(status__status="canceled")

    # 4) Count codes
    reserved_counts = Counter(reserved_qs.values_list("reservation_code", flat=True))
    canceled_counts = Counter(canceled_qs.values_list("reservation_code", flat=True))

    # 5) Which codes still have net > 0?
    active_codes = [
        code
        for code, cnt in reserved_counts.items()
        if cnt > canceled_counts.get(code, 0)
    ]

    # 6) For each active code, grab its latest “reserved” record
    active_reservations = []
    for code in active_codes:
        rec = (
            future_qs.filter(reservation_code=code)
            .order_by("-date_status_updated")
            .first()
        )
        if rec:
            active_reservations.append(rec)

    # 7) Generate SVG QR for each
    for res in active_reservations:
        qr = qrcode.QRCode(box_size=4, border=1)
        qr.add_data(res.reservation_code)
        qr.make(fit=True)
        img = qr.make_image(image_factory=SvgPathImage)

        buf = io.BytesIO()
        img.save(buf)
        res.qr_svg = buf.getvalue().decode("utf-8")

    return render(
        request,
        "reserved.html",
        {
            "reservations": active_reservations,
            "profile": profile,
        },
    )


# ==========================================
#
#               ADMIN PANEL
#
# ==========================================


def is_admin(user):
    return user.is_authenticated and user.is_staff


@user_passes_test(is_admin)
def admin(request):
    return redirect("/")


@user_passes_test(is_admin)
def admin_dashboard(request):
    return render(
        request, "admin/admin-dashboard.html", {"active_page": "admin-dashboard"}
    )


@user_passes_test(is_admin)
def admin_users(request):
    return render(request, "admin/admin-users.html", {"active_page": "admin-users"})


@user_passes_test(is_admin)
def admin_password_recovery_requests(request):
    if request.method == "POST":
        req_id = request.POST.get("id")
        status = request.POST.get("fulfilled") == "true"

        recovery = get_object_or_404(RecoveryRequest, id=req_id)
        recovery.fulfilled = status
        recovery.save()

        return redirect(f"{reverse('admin_password_recovery_requests')}?success=1")

    query = request.GET.get("q", "").strip()
    recovery_requests = RecoveryRequest.objects.all()

    if query:
        terms = query.split()
        for term in terms:
            fulfilled_lookup = None
            if "پاسخ" in term or "داده شد" in term:
                fulfilled_lookup = True
            elif "در حال" in term or "انجام" in term:
                fulfilled_lookup = False

            conditions = (
                Q(user__first_name__icontains=term)
                | Q(user__last_name__icontains=term)
                | Q(user__email__icontains=term)
                | Q(user__username__icontains=term)
                | Q(user__profile__phone_number__icontains=term)
                | Q(created_at__icontains=term)
            )

            if fulfilled_lookup is not None:
                conditions |= Q(fulfilled=fulfilled_lookup)

            recovery_requests = recovery_requests.filter(conditions)

    show_notification = request.GET.get("success") == "1"

    return render(
        request,
        "admin/admin-password-recovery-requests.html",
        {
            "active_page": "admin-password-recovery-requests",
            "requests": recovery_requests,
            "notification": show_notification,
            "notification_status": True,
            "notification_message": "با موفقیت ثبت شد!" if show_notification else "",
        },
    )


@user_passes_test(is_admin)
def admin_foods(request):
    if request.method == "POST":
        food_id = request.POST.get("id")
        name = request.POST.get("name")
        description = request.POST.get("description")
        image = request.FILES.get("image")

        if food_id:  # Edit
            food = get_object_or_404(Food, id=food_id)
            food.name = name
            food.description = description
            if image:
                food.image = image
            food.save()
        else:  # New
            Food.objects.create(name=name, description=description, image=image)

        return redirect(f"{reverse('admin_foods')}?success=1")

    query = request.GET.get("q", "").strip()
    foods = Food.objects.all()

    if query:
        terms = query.split()
        for term in terms:
            foods = foods.filter(
                Q(name__icontains=term)
                | Q(description__icontains=term)
                | Q(image__icontains=term)
            )

    show_notification = request.GET.get("success") == "1"
    return render(
        request,
        "admin/admin-foods.html",
        {
            "active_page": "admin-foods",
            "foods": foods,
            "notification": show_notification,
            "notification_status": True,
            "notification_message": "با موفقیت ثبت شد!" if show_notification else "",
        },
    )


@csrf_exempt
@user_passes_test(is_admin)
def delete_food(request, id):
    if request.method == "POST":
        food = get_object_or_404(Food, id=id)
        food.delete()
        return HttpResponse(status=200)
    return HttpResponseNotAllowed(["POST"])


@csrf_exempt
@user_passes_test(is_admin)
def admin_drinks(request):
    if request.method == "POST":
        drink_id = request.POST.get("id")
        name = request.POST.get("name")
        desc = request.POST.get("description")

        if drink_id:  # Edit
            drink = get_object_or_404(Drink, id=drink_id)
            drink.name = name
            drink.description = desc
            drink.save()
        else:  # New
            Drink.objects.create(name=name, description=desc)

        return redirect(f"{reverse('admin_drinks')}?success=1")

    query = request.GET.get("q", "").strip()
    drinks = Drink.objects.all()

    if query:
        terms = query.split()  # Split by spaces
        for term in terms:
            # Add filter for any field matching this term (case insensitive)
            drinks = drinks.filter(
                Q(name__icontains=term) | Q(description__icontains=term)
            )

    show_notification = request.GET.get("success") == "1"
    return render(
        request,
        "admin/admin-drinks.html",
        {
            "active_page": "admin-drinks",
            "drinks": drinks,
            "notification": show_notification,
            "notification_status": True,
            "notification_message": "با موفقیت ثبت شد!" if show_notification else "",
        },
    )


@csrf_exempt
@user_passes_test(is_admin)
def delete_drink(request, id):
    if request.method == "POST":
        drink = get_object_or_404(Drink, id=id)
        drink.delete()
        return HttpResponse(status=200)
    return HttpResponseNotAllowed(["POST"])


@csrf_exempt
@user_passes_test(is_admin)
def admin_sidedishes(request):
    if request.method == "POST":
        sidedish_id = request.POST.get("id")
        name = request.POST.get("name")
        desc = request.POST.get("description")

        if sidedish_id:  # Edit
            sidedish = get_object_or_404(SideDish, id=sidedish_id)
            sidedish.name = name
            sidedish.description = desc
            sidedish.save()
        else:  # New
            SideDish.objects.create(name=name, description=desc)

        return redirect(f"{reverse('admin_sidedishes')}?success=1")

    query = request.GET.get("q", "").strip()
    sidedishes = SideDish.objects.all()

    if query:
        terms = query.split()
        for term in terms:
            sidedishes = sidedishes.filter(
                Q(name__icontains=term) | Q(description__icontains=term)
            )

    show_notification = request.GET.get("success") == "1"
    return render(
        request,
        "admin/admin-sidedishes.html",
        {
            "active_page": "admin-sidedishes",
            "sidedishes": sidedishes,
            "notification": show_notification,
            "notification_status": True,
            "notification_message": "با موفقیت ثبت شد!" if show_notification else "",
        },
    )


@csrf_exempt
@user_passes_test(is_admin)
def delete_sidedish(request, id):
    if request.method == "POST":
        sidedish = get_object_or_404(SideDish, id=id)
        sidedish.delete()
        return HttpResponse(status=200)
    return HttpResponseNotAllowed(["POST"])


@user_passes_test(is_admin)
def admin_daily_menu_items(request):
    return render(
        request,
        "admin/admin-daily-menu-items.html",
        {"active_page": "admin-daily-menu-items"},
    )


@user_passes_test(is_admin)
def admin_reservations(request):
    query = request.GET.get("q", "").strip()
    reservations = Reservation.objects.select_related(
        "user", "status", "dailymenu__food", "dailymenu__drink"
    ).prefetch_related("dailymenu__side_dishes")

    if query:
        terms = query.split()
        for term in terms:
            status_value = {
                "رزرو شده": "reserved",
                "مصرف شده": "used",
                "لغو شده": "canceled",
                "منقضی شده": "expired",
            }.get(term)

            filters = (
                Q(user__first_name__icontains=term)
                | Q(user__last_name__icontains=term)
                | Q(user__username__icontains=term)
                | Q(user__email__icontains=term)
                | Q(reservation_code__icontains=term)
                | Q(status__title__icontains=term)
                | Q(dailymenu__food__name__icontains=term)
                | Q(dailymenu__drink__name__icontains=term)
                | Q(dailymenu__side_dishes__name__icontains=term)
            )

            if status_value:
                filters |= Q(status__status__iexact=status_value)

            reservations = reservations.filter(filters)

        reservations = reservations.distinct()

    return render(
        request,
        "admin/admin-reservations.html",
        {
            "active_page": "admin-reservations",
            "reservations": reservations,
        },
    )


@user_passes_test(is_admin)
def admin_guests(request):
    return render(request, "admin/admin-guests.html", {"active_page": "admin-guests"})
