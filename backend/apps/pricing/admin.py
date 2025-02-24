from django.contrib import admin

# Register your models here.

from apps.pricing.models import Product, Price

admin.site.register(Product)
admin.site.register(Price)
