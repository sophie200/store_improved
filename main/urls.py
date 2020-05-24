from django.urls import path, include
from django.contrib.auth import views as auth_views
from . views import (
    HomePageView,
    AboutPageView,
    SignupView,
    ProductTagsView,
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
    path('logout/', views.logout_view, name="logout"),
    path('products/', ProductTagsView.as_view(), name = "tags"),
    path('products/<slug:tag>/', ProductListView.as_view(), name="products"),
    path('product/<slug:slug>/', DetailView.as_view(model=models.Product), name="product"),
    path('add_to_basket/', views.add_to_basket, name="add_to_basket"),
    path('basket/', views.manage_basket, name="basket"),
    path('address/', views.AddressListView.as_view(), name="addressupdate_list"),
    path('address/create/', views.AddressCreateView.as_view(), name="address_create"),
    path('address/<int:pk>/', views.AddressUpdateView.as_view(), name="address_update"),
    path('address/<int:pk>/delete/', views.AddressDeleteView.as_view(), name="address_delete"),
    path('order/address_select/', views.AddressSelectionView.as_view(), name="address_select"),
    path('order/done/', OrderDoneView.as_view(), name="checkout_done"),
]
