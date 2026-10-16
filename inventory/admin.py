from django.contrib import admin
from .models import Category, Customer, Expense, Product, Purchase, ReturnRecord, Sale, StockMovement, Supplier

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "sku", "category", "supplier", "price", "stock", "reorder_level", "is_active")
    list_filter = ("category", "is_active")
    search_fields = ("name", "sku")
    list_editable = ("price", "stock", "reorder_level", "is_active")

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ("name",)

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "email")
    search_fields = ("name", "phone", "email")

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "email")
    search_fields = ("name", "phone", "email")

admin.site.register(Purchase)
admin.site.register(Sale)
admin.site.register(Expense)
admin.site.register(ReturnRecord)
admin.site.register(StockMovement)
