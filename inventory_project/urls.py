# FOR MORE REAL TIME PROJECTS VISIT :- https://updategadh.com/ 
# Developed By UPDATEGADH TEAM

from django.urls import path
from inventory import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("products/", views.products, name="products"),
    path("products/add/", views.product_add, name="product_add"),
    path("products/delete/<int:pk>/", views.product_delete, name="product_delete"),
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
]
