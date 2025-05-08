from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.db.models import Q, Count, Case, When, IntegerField, F

from django.contrib.auth import login, authenticate
from pages.forms import LoginForm, RecoveryForm

from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required

from django.utils import timezone
import jdatetime

from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST

import hashlib, random

from users.models import Profile, RecoveryRequest
from daily_menus.models import DailyMenuItem
from reservations.models import Reservation, Status

class LoginViewPage(LoginView):
    template_name = 'index.htm'
    form_class = LoginForm


@login_required
def logout(request):
    from django.contrib.auth import logout
    from django.shortcuts import redirect

    logout(request)
    return redirect('/')


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
                RecoveryRequest.objects.create(
                    user=profile.user,
                    **answers
                )

            # Always show the same generic message, whether or not we found a match
            messages.success(
                request,
                "Thank you. If your answers match one of our records, an administrator will contact you shortly."
            )
            return render(request, template_name="user-password-recovery.htm",
                          context={'form': form, 'notification': True, 'notification_status': True,
                                   'notification_message': 'با موفقیت ثبت شد!'})
    else:
        form = RecoveryForm()

    return render(request, template_name="user-password-recovery.htm", context={'form': form})


@login_required
def dashboard(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    return render(request, template_name="dashboard.htm", context={'profile': profile})

@login_required
def ajax_wallet_balance(request):
    profile = request.user.profile
    # return integer or string formatted as you like
    return JsonResponse({
        'balance': profile.wallet_balance,
        'formatted': f"{profile.wallet_balance:,}"
    })

@login_required
def reserve(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    currentDate = jdatetime.datetime.now()

    today_menu = DailyMenuItem.objects.filter(
        expiration_date__date=currentDate.date()
    )

    # Annotate each item with net reserved count for this user & this item & this date:
    #   #reserves – #cancels
    reservations = (
        Reservation.objects
        .filter(
            user=request.user,
            dailymenu__in=today_menu,
            dailymenu__expiration_date__date=currentDate.date()
        )
        .values('dailymenu')
        .annotate(
            net=Count(
                Case(When(status__status='reserved', then=1), output_field=IntegerField())
            )
                - Count(
                Case(When(status__status='canceled', then=1), output_field=IntegerField())
            )
        )
    )
    # Build a lookup: { menu_id: net_count, ... }
    reserved_map = {r['dailymenu']: r['net'] for r in reservations}

    # Now inject max_purchasable_quantity = 0 if past deadline, and reserve_count
    for item in today_menu:
        if item.reservation_deadline <= timezone.make_aware(
                item.reservation_deadline.togregorian(), timezone.get_current_timezone()):
            item.max_purchasable_quantity = 0
        item.reserved_count = reserved_map.get(item.id, 0)

    return render(request, "reserve.htm", {
        'profile': profile,
        'todayMenu': today_menu,
        'currentDate': currentDate.timestamp()
    })

@login_required
@require_GET
def get_meals_by_timestamp(request):
    ts = request.GET.get('timestamp')
    if not ts:
        return JsonResponse({'error': 'Missing timestamp'}, status=400)

    try:
        ts = int(float(ts))
    except ValueError:
        return JsonResponse({'error': 'Invalid timestamp format'}, status=400)

    # build the date to filter on
    dt = jdatetime.datetime.fromtimestamp(ts)
    date = dt.date()

    # fetch the day's menu
    meals = DailyMenuItem.objects.filter(expiration_date__date=date)

    # compute net reserved vs canceled for this user & date
    reservations = (
        Reservation.objects
        .filter(
            user=request.user,
            dailymenu__in=meals,
            dailymenu__expiration_date__date=date
        )
        .values('dailymenu')
        .annotate(
            net=Count(
                Case(When(status__status='reserved', then=1)),
                output_field=IntegerField()
            )
            - Count(
                Case(When(status__status='canceled', then=1)),
                output_field=IntegerField()
            )
        )
    )
    reserved_map = { r['dailymenu']: r['net'] for r in reservations }

    # chosen “now” for deadline checks
    now_aware = timezone.make_aware(
        jdatetime.datetime.now().togregorian(),
        timezone.get_current_timezone()
    )

    meal_data = []
    for item in meals:
        # enforce deadline
        max_q = item.max_purchasable_quantity if item.reservation_deadline >= now_aware else 0
        # how many already reserved
        reserved_count = reserved_map.get(item.id, 0)

        meal_data.append({
            'id':             item.id,
            'name':           item.food.name,
            'description':    "، ".join(str(s) for s in item.side_dishes.all()),
            'price':          item.price,
            'image_url':      item.image.url,
            'max_qty':        max_q,
            'reserved_count': reserved_count,
        })

    return JsonResponse({'meals': meal_data})

@login_required
@require_POST
def ajax_reserve(request):
    user = request.user
    menu_id = request.POST.get('menu_id')
    try:
        menu_item = DailyMenuItem.objects.select_for_update().get(pk=int(menu_id))
    except (ValueError, DailyMenuItem.DoesNotExist):
        return JsonResponse({'error': 'Invalid menu item.'}, status=400)

    # check stock
    if menu_item.quantity < 1:
        return JsonResponse({'error': 'Out of stock.'}, status=400)

    # check wallet
    if user.profile.wallet_balance < menu_item.price:
        return JsonResponse({'error': 'Insufficient balance.'}, status=400)

    reserved_status = Status.objects.get(status='reserved')

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
            return JsonResponse({'error': 'Try again later.'}, status=500)

        Reservation.objects.create(
            user=user,
            dailymenu=menu_item,
            status=reserved_status,
            reservation_code=code
        )

    return JsonResponse({'success': True, 'new_qty': menu_item.quantity, 'code': code})


@login_required
@require_POST
def ajax_cancel(request):
    user = request.user
    menu_id = request.POST.get('menu_id')
    try:
        menu_item = DailyMenuItem.objects.select_for_update().get(pk=int(menu_id))
    except (ValueError, DailyMenuItem.DoesNotExist):
        return JsonResponse({'error': 'Invalid menu item.'}, status=400)

    canceled_status = Status.objects.get(status='canceled')

    # find one existing 'reserved' reservation to cancel, for this user & item & date
    orig = (Reservation.objects
            .filter(user=user, dailymenu=menu_item, status__status='reserved',
                    dailymenu__expiration_date=menu_item.expiration_date)
            .order_by('-date_status_updated')
            .first())
    if not orig:
        return JsonResponse({'error': 'No active reservation found.'}, status=400)

    # generate a new code for the cancellation record
    raw = f"{user.id}-{menu_id}-cancel-{timezone.now().timestamp()}-{random.random()}"
    num = int(hashlib.sha256(raw.encode()).hexdigest(), 16) % 10**8
    code = f"{num:08d}"

    with transaction.atomic():
        # restore stock & wallet
        menu_item.quantity += 1
        menu_item.save()

        profile = user.profile
        profile.wallet_balance += menu_item.price
        profile.save()

        Reservation.objects.create(
            user=user,
            dailymenu=menu_item,
            status=canceled_status,
            reservation_code=code
        )

    return JsonResponse({'success': True, 'new_qty': menu_item.quantity, 'code': code})

@login_required
def reserved(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    return render(request, template_name="reserved.htm", context={'profile': profile})
