from django.contrib import admin
from .models import Product, Collection, Cart
# Register your models here.


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'collection')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id',)


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
