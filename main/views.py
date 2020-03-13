from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.views.generic.edit import (
    FormView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.views.generic.list import ListView
from django.shortcuts import get_object_or_404, render
from . import forms
from . import models

from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    UserPassesTestMixin,
)
from django import forms as django_forms
from django.db import models as django_models

class HomePageView(TemplateView):
    template_name = 'home.html'

class AboutPageView(TemplateView):
    template_name = 'about.html'

class SignupView(FormView):
    template_name = "signup.html"
    form_class = forms.UserCreationForm

    def get_success_url(self):
        redirect_to = self.request.GET.get("next", "/")
        return redirect_to

    def form_valid(self, form):
        response = super().form_valid(form)
        form.save()

        email = form.cleaned_data.get("email")
        raw_password = form.cleaned_data.get("password1")

        user = authenticate(email=email, password=raw_password)
        login(self.request, user)

        form.send_mail()

        messages.info(
            self.request, "You signed up successfully."
        )

        return response

class ProductListView(ListView):
    template_name = "product_list.html"
    paginate_by = 4

    def get_queryset(self):
        tag = self.kwargs["tag"]
        self.tag = None

        if tag != "all":
            self.tag = get_object_or_404(
                models.ProductTag, slug=tag
            )

        if self.tag:
            products = models.Product.objects.active().filter(
                tags=self.tag
            )
        else:
            products = models.Product.objects.active()

        return products.order_by("name")

def add_to_basket(request):
    product = get_object_or_404(
        models.Product, pk=request.GET.get("product_id")
    )
    basket = request.basket
    if not request.basket:
        if request.user.is_authenticated:
            user = request.user
        else:
            user = None
        basket = models.Basket.objects.create(user=user)
        request.session["basket_id"] = basket.id

    basketline, created = models.BasketLine.objects.get_or_create(
        basket=basket, product=product
    )
    if not created:
        basketline.quantity += 1
        basketline.save()
    return HttpResponseRedirect(
        reverse("product", args=(product.slug,))
    )

def manage_basket(request):
    if not request.basket:
        return render(request, "basket.html", {"formset": None})

    if request.method == "POST":
        formset = forms.BasketLineFormSet(
            request.POST, instance=request.basket
        )
        if formset.is_valid():
            formset.save()
    else:
        formset = forms.BasketLineFormSet(
            instance=request.basket
        )

    if request.basket.is_empty():
        return render(request, "basket.html", {"formset": None})

    return render(request, "basket.html", {"formset": formset})

class OrderConfirmView(LoginRequiredMixin, FormView):
    template_name = "order_confirm.html"
    form_class = forms.OrderConfirmForm
    success_url = reverse_lazy("checkout_done")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        del self.request.session["basket_id"]
        basket = self.request.basket
        basket.create_order()
        return super().form_valid(form)

class OrderDoneView(TemplateView):
    template_name = 'order_done.html'
