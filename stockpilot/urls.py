from django.contrib import admin
from django.urls import path
from inventory import views

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("", views.dashboard, name="dashboard"),
    path("products/", views.products, name="products"),
    path("products/add/", views.product_add, name="product_add"),
    path("products/<int:pk>/edit/", views.product_edit, name="product_edit"),
    path("products/<int:pk>/delete/", views.product_delete, name="product_delete"),
    path("categories/", views.categories, name="categories"),
    path("categories/add/", views.category_add, name="category_add"),
    path("categories/<int:pk>/edit/", views.category_edit, name="category_edit"),
    path("suppliers/", views.suppliers, name="suppliers"),
    path("suppliers/add/", views.supplier_add, name="supplier_add"),
    path("customers/", views.customers, name="customers"),
    path("customers/add/", views.customer_add, name="customer_add"),
    path("purchases/", views.purchases, name="purchases"),
    path("purchases/add/", views.purchase_add, name="purchase_add"),
    path("sales/", views.sales, name="sales"),
    path("sales/add/", views.sale_add, name="sale_add"),
    path("expenses/", views.expenses, name="expenses"),
    path("expenses/add/", views.expense_add, name="expense_add"),
    path("returns/", views.returns, name="returns"),
    path("returns/add/", views.return_add, name="return_add"),
    path("reports/export/products.csv", views.export_products_csv, name="export_products_csv"),
]
