from decimal import Decimal
from django.db import models
from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,   
)

# Create your models here.
class Role(models.Model):
    """User roles."""
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=70)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class UserManager(BaseUserManager):
    """Manager for users."""

    def create_user(self, email, password=None, **extra_fields):
        """Create, save and return a new user."""
        if not email:
            raise ValueError('User must have an email address.')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Create and return a new superuser."""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    role = models.ForeignKey(Role, on_delete=models.PROTECT, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    username = None
    objects = UserManager()

    USERNAME_FIELD = 'email'

    def __str__(self):
        return str(self.first_name) + " " + str(self.last_name)


class UserToken(models.Model):
    user_id = models.IntegerField()
    token = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField()


class Reset(models.Model):
    email = models.CharField(max_length=255)
    token = models.CharField(max_length=255, unique=True)


class Customer(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    contact_no = models.CharField(max_length=120, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.first_name) + " " + str(self.last_name)


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Supplier(models.Model):
    company_name = models.CharField(max_length=150, unique=True)
    description =  models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    contact_no = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.company_name


class Product(models.Model):
    product_code = models.IntegerField(unique=True)
    name = models.CharField(max_length=255, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    qty_on_hand = models.IntegerField(default=0)
    price= models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='product_images', blank=True, null=True)
    date_stock_in = models.DateField(auto_now=False, auto_now_add=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    # created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Transaction(models.Model):
    transaction_code = models.IntegerField(unique=True, null=True)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    items_quantity = models.IntegerField(default=0)
    tax = models.DecimalField(max_digits=100, decimal_places=2, default=Decimal('0.00'),  null=True)
    # created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    total_price = models.DecimalField(max_digits=7, decimal_places=2, default=Decimal('0.00'), null=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return self.transaction_code


class Transaction_Item(models.Model):
    transaction = models.ForeignKey(Transaction,
                                         related_name='transaction_items', 
                                         on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, related_name='transaction_products',
                                         on_delete=models.CASCADE, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'),)
    quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return str(self.id)