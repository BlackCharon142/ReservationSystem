from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from django.contrib.auth import login, authenticate
from pages.forms import LoginForm, RecoveryForm

from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required

import jdatetime

from django.http import JsonResponse
from django.views.decorators.http import require_GET

from users.models import Profile, RecoveryRequest
from daily_menus.models import DailyMenuItem

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
def reserve(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    currentDate = jdatetime.datetime.now()
    today_menu = DailyMenuItem.objects.filter(expiration_date__date=currentDate.date())
    print(currentDate.date())
    return render(request, template_name="reserve.htm", context={'profile': profile, 'todayMenu': today_menu, 'currentDate': currentDate.timestamp()})

@require_GET
def get_meals_by_timestamp(request):
    try:
        ts = request.GET.get('timestamp')
        if not ts:
            return JsonResponse({'error': 'Missing timestamp'}, status=400)

        # Fix: Convert float string to int safely
        try:
            ts = int(float(ts))
        except ValueError:
            return JsonResponse({'error': 'Invalid timestamp format'}, status=400)
        # Convert to datetime
        dt = jdatetime.datetime.fromtimestamp(ts)
        date = dt.date()  # only the date part

        meals = DailyMenuItem.objects.filter(expiration_date__date=date)
        print(date)
        meal_data = []
        for item in meals:
            meal_data.append({
                'id': item.id,
                'name': item.food.name,
                'description': "، ".join([str(s) for s in item.side_dishes.all()]),
                'price': item.price,
                'image_url': item.image.url,
                'max_qty': item.max_purchasable_quantity,
            })

        return JsonResponse({'meals': meal_data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def reserved(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    return render(request, template_name="reserved.htm", context={'profile': profile})
