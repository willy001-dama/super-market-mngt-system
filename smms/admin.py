from django.contrib import admin

# Register your models here.
from .models import Product, Sale, TotalProduct,\
    Profile, Investment, TotalSalesPrice, OrderItem, Order,\
    Message


class ProductAdmin(admin.ModelAdmin):
    search_fields = ['name', 'category']
    list_display = ['name', 'category', 'quantity', 'date']
    list_filter = ['date', 'name']


admin.site.register(Product, ProductAdmin)
admin.site.register(Sale)
admin.site.register(TotalProduct)
admin.site.register(Profile)
admin.site.register(Investment)
admin.site.register(TotalSalesPrice)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Message)
