from django.db import models

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

default_value = timezone.now


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=400)
    image = models.ImageField(upload_to='category_images/', default='category_images/default.jpg')

    def __str__(self):
        return self.name
        
# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=500)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/')  # You can specify a different upload path if needed
    quantity = models.IntegerField(default=0)  # Specify your desired default value here
    vendor = models.CharField(max_length=20)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    original_price = models.FloatField(blank=False, default=0.0)
    selling_price = models.FloatField(blank=False, default=0.0)
    status = models.BooleanField(default=False, help_text='0-show, 1-Hidden')
    trending = models.BooleanField(default=False, help_text='0-default, 1-Trending')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def total_price(self):
        return self.quantity * self.product.price
# name,phone,email,passwords,address,profile,

from django.db import models

class user_register(models.Model):
    Name = models.CharField(max_length=60)
    Phone = models.CharField(max_length=10)  # Change to CharField for phone numbers
    Email = models.EmailField(max_length=255)
    Password = models.CharField(max_length=20)
    Address = models.CharField(max_length=300)
    Profile = models.ImageField(upload_to='profile/')

    def __str__(self):
        return self.Name

# models.py

from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)

    def __str__(self):
        return f"Profile of {self.user.username}"
