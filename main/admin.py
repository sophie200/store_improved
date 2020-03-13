from django.contrib import admin
from django.contrib.auth.admin import (
    UserAdmin as DjangoUserAdmin
)
from . import models

@admin.register(models.User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Personal info",
            {"fields": ("first_name", "last_name")},
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            "Important dates",
            {"fields": ("last_login", "date_joined")},
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )
    list_display = (
        "email",
        "first_name",
        "last_name",
        "is_staff",
    )
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)

@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "in_stock", "price",)
    list_filter = ("active", "in_stock", "date_updated",)
    list_editable = ("in_stock",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ("tags",)

@admin.register(models.ProductTag)
class ProductTagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    list_filter = ("active",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}

@admin.register(models.ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("thumbnail_tag", "product_name")
    readonly_fields = ("thumbnail",)
    search_fields = ("product__name",)

    def thumbnail_tag(self, obj):
        if obj.thumbnail:
            return format_html(
                '<img src="%s"/>' % obj.thumbnail.url
            )
        return "-"

    thumbnail_tag.short_description = "Thumbnail"

    def product_name(self, obj):
        return obj.product.name

class BasketLineInline(admin.TabularInline):
    model = models.BasketLine
    raw_id_fields = ("product",)

@admin.register(models.Basket)
class BasketAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "count")
    list_editable = ("status",)
    list_filter = ("status",)
    inlines = (BasketLineInline,)

class OrderLineInline(admin.TabularInline):
    model = models.OrderLine
    raw_id_fields = ("product",)

@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status")
    list_editable = ("status",)
    list_filter = ("status", "date_added")
    inlines = (OrderLineInline,)
    fieldsets = (
        (None, {"fields": ("user", "status")}),
    )
