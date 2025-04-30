from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User


class LoginForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ['username', 'password']

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = 'نام کاربری'
        self.fields['password'].label = 'رمز عبور'
        self.fields['username'].widget.attrs.update({'class': 'text'})
        self.fields['password'].widget.attrs.update({'class': 'text'})


class RecoveryForm(forms.Form):
    answer_1 = forms.CharField(
        max_length=255,
        widget=forms.PasswordInput(attrs={'class': 'text'}),
        label="نام بهترین دوست دوران کودکیتان چه بود؟",
    )
    answer_2 = forms.CharField(
        max_length=255,
        widget=forms.PasswordInput(attrs={'class': 'text'}),
        label="مدل یا برند اولین وسیله نقلیه تان چه بود؟"
    )
    answer_3 = forms.CharField(
        max_length=255,
        widget=forms.PasswordInput(attrs={'class': 'text'}),
        label="نام حیوان خانگی محبوبتان در دوران کودکی چه بود؟"
    )
    answer_4 = forms.CharField(
        max_length=255,
        widget=forms.PasswordInput(attrs={'class': 'text'}),
        label="نام خیابانی که اولین خانه تان در آن قرار داشت چه بود؟"
    )
    answer_5 = forms.CharField(
        max_length=255,
        widget=forms.PasswordInput(attrs={'class': 'text'}),
        label="نام معلم مورد علاقه تان در دوران تحصیل چه بود؟"
    )
