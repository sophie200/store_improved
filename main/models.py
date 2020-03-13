from django.contrib.auth.models import (
    AbstractUser,
    BaseUserManager,
)
from django.db import models
from django.core.validators import MinValueValidator
from django.db.models import Count, Sum
from django.urls import reverse

class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(
                "Superuser must have is_staff=True."
            )
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(
                "Superuser must have is_superuser=True."
            )

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField("email address", unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

class ProductTagManager(models.Manager):
    def get_by_natural_key(self, slug):
        return self.get(slug=slug)

class ProductTag(models.Model):
    name = models.CharField(max_length=40)
    slug = models.SlugField(max_length=48)
    description = models.TextField(blank=True)
    active = models.BooleanField(default=True)

    objects = ProductTagManager()

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.slug,)

class ActiveManager(models.Manager):
    def active(self):
        return self.filter(active=True)

class Product(models.Model):
    name = models.CharField(max_length=40)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    slug = models.SlugField(max_length=48)
    tags = models.ManyToManyField(ProductTag, blank=True)
    active = models.BooleanField(default=True)
    in_stock = models.BooleanField(default=True)
    date_updated = models.DateTimeField(auto_now=True)

    objects = ActiveManager()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('product', args=[str(self.slug)])

class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to="product-images")
    thumbnail = models.ImageField(
        upload_to="product-thumbnails", null=True
    )

class Basket(models.Model):
    OPEN = 10
    SUBMITTED = 20
    STATUSES = ((OPEN, "Open"), (SUBMITTED, "Submitted"))
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=True, null=True
    )
    status = models.IntegerField(choices=STATUSES, default=OPEN)

    def is_empty(self):
        return self.basketline_set.all().count() == 0

    def count(self):
        return sum(i.quantity for i in self.basketline_set.all())

    def create_order(self):
        if not self.user:
            raise exceptions.BasketException(
                "Cannot create order without user"
            )

        order_data = self.user
        order = Order.objects.create(user=order_data)
        c = 0
        for line in self.basketline_set.all():
            for item in range(line.quantity):
                order_line_data = {
                    "order": order,
                    "product": line.product,
                }
                order_line = OrderLine.objects.create(
                    **order_line_data
                )
                c += 1

        self.status = Basket.SUBMITTED
        self.save()
        return order

class BasketLine(models.Model):
    basket = models.ForeignKey(Basket, on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(
        default=1, validators=[MinValueValidator(1)]
    )

class Order(models.Model):
    NEW = 10
    ORDERED = 20
    DONE = 30
    STATUSES = ((NEW, "New"), (ORDERED, "Ordered"), (DONE, "Done"))
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.IntegerField(choices=STATUSES, default=NEW)

    date_updated = models.DateTimeField(auto_now=True)
    date_added = models.DateTimeField(auto_now_add=True)

class OrderLine(models.Model):
    NEW = 10
    PROCESSING = 20
    ORDERED = 30
    CANCELLED = 40
    STATUSES = (
        (NEW, "New"),
        (PROCESSING, "Processing"),
        (ORDERED, "Ordered"),
        (CANCELLED, "Cancelled"),
    )

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="lines"
    )
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT
    )
    status = models.IntegerField(choices=STATUSES, default=NEW)
