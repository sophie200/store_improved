from django.urls import path, include
from django.contrib.auth import views as auth_views
from . views import (
    HomePageView,
    AboutPageView,
    SignupView,
    ProductListView,
    OrderDoneView,
)
from django.views.generic.detail import DetailView
from . import forms, models, views

urlpatterns = [
    path('', HomePageView.as_view(), name="home"),
    path('about/', AboutPageView.as_view(), name="about"),
    path('signup/', SignupView.as_view(), name="signup"),
    path('login/', auth_views.LoginView.as_view(template_name="login.html", form_class=forms.AuthenticationForm), name="login"),
    path('logout/', auth_views.LogoutView.as_view(template_name="logout.html"), name="logout"),
    path('products/<slug:tag>/', ProductListView.as_view(), name="products"),
    path('product/<slug:slug>/', DetailView.as_view(model=models.Product), name="product"),
    path('add_to_basket/', views.add_to_basket, name="add_to_basket"),
    path('basket/', views.manage_basket, name="basket"),
    path('order/order_confirm/', views.OrderConfirmView.as_view(), name="order_confirm"),
    path('order/done/', OrderDoneView.as_view(), name="checkout_done"),
]
