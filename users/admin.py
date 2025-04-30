from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from django import forms
from .models import Profile, RecoveryRequest

admin.site.register(Profile)

class ProfileInlineForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('image','phone_number', 'wallet_balance',
                  'security_answer_1','security_answer_2',
                  'security_answer_3','security_answer_4',
                  'security_answer_5')
        labels = {
            'security_answer_1': 'نام بهترین دوست دوران کودکیتان چه بود؟',
            'security_answer_2': 'مدل یا برند اولین وسیله نقلیه تان چه بود؟',
            'security_answer_3': 'نام حیوان خانگی محبوبتان در دوران کودکی چه بود؟',
            'security_answer_4': 'نام خیابانی که اولین خانه تان در آن قرار داشت چه بود؟',
            'security_answer_5': 'نام معلم مورد علاقه تان در دوران تحصیل چه بود؟',
        }
        widgets = {
            'security_answer_1': forms.PasswordInput(render_value=True),
            'security_answer_2': forms.PasswordInput(render_value=True),
            'security_answer_3': forms.PasswordInput(render_value=True),
            'security_answer_4': forms.PasswordInput(render_value=True),
            'security_answer_5': forms.PasswordInput(render_value=True),
        }

    def clean(self):
        cleaned = super().clean()
        # ensure all five are nonblank
        for i in range(1,6):
            if not cleaned.get(f"security_answer_{i}"):
                self.add_error(
                    f"security_answer_{i}", "This field is required."
                )
        return cleaned

class ProfileInline(admin.StackedInline):
    model = Profile
    form = ProfileInlineForm
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'

# unregister the old User admin, then re-register
admin.site.unregister(User)

@admin.register(User)
class UserAdmin(DefaultUserAdmin):
    inlines = (ProfileInline,)

    # ========== OVERRIDE ADD USER FORM ==========
    add_fieldsets = (
        (None, {
            'classes': ('wide',),  # makes the form a bit wider
            'fields': (
                'username',
                'first_name',  # show First name
                'last_name',  # show Last name
                'email',  # show Email address
                'password1',
                'password2',
            ),
        }),
    )
    # ============================================
    # So you see the avatar thumbnail already:
    list_display = DefaultUserAdmin.list_display + ('get_avatar_thumb',)
    readonly_fields = ('get_avatar_thumb',)

    def get_avatar_thumb(self, obj):
        if hasattr(obj, 'profile') and obj.profile.image:
            return mark_safe(
                f'<img src="{obj.profile.image.url}" width="40" height="40" '
                'style="border-radius:50%;" />'
            )
        return "-"
    get_avatar_thumb.short_description = 'Avatar'


@admin.register(RecoveryRequest)
class RecoveryRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'fulfilled')
    list_filter = ('fulfilled', 'created_at', 'user')
    actions = ['mark_fulfilled']

    @admin.action(description="Mark selected requests as fulfilled")
    def mark_fulfilled(self, request, queryset):
        updated = queryset.update(fulfilled=True)
        self.message_user(request,
                          f"{updated} request(s) marked fulfilled."
                          )
