from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import (
    UserCreationForm as DjangoUserCreationForm
)
from django.contrib.auth.forms import UsernameField
from django.core.mail import send_mail
from django.forms import inlineformset_factory

from . import models, widgets

class UserCreationForm(DjangoUserCreationForm):
    class Meta(DjangoUserCreationForm.Meta):
        model = models.User
        fields = ("email",)
        field_classes = {"email": UsernameField}

    def send_mail(self):
        message = "Welcome {}".format(self.cleaned_data["email"])
        send_mail(
            "Welcome to BookTime",
            message,
            "site@booktime.domain",
            [self.cleaned_data["email"]],
            fail_silently=True,
        )

class AuthenticationForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(
        strip=False, widget=forms.PasswordInput
    )

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user = None
        super().__init__(*args, **kwargs)

    def clean(self):
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")

        if email is not None and password:
            self.user = authenticate(
                self.request, email=email, password=password
            )
            if self.user is None:
                raise forms.ValidationError(
                    "Invalid email/password combination."
                )
        return self.cleaned_data

    def get_user(self):
        return self.user

BasketLineFormSet = inlineformset_factory(
    models.Basket,
    models.BasketLine,
    fields=("quantity",),
    extra=0,
    widgets={"quantity": widgets.PlusMinusNumberInput()},
)

class OrderConfirmForm(forms.Form):
    name = forms.CharField(label="Confirm your order below. If you want tell us how your day has been in the space below!", max_length=10000)

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def send_mail(self):
        message = "From: {0}\n{1}".format(
            self.cleaned_data["name"],
        )
        send_mail(
            "Site message",
            message,
            "wy@crochet.com",
            ["customerservice@crochet.com"],
            fail_silently=False,
        )
