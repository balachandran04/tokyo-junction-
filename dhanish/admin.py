from django.contrib import admin
from .models import Product, Category,user_register

admin.site.register(Product)
admin.site.register(Category)
admin.site.register(user_register)