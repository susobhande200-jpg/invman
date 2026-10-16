# FOR MORE REAL TIME PROJECTS VISIT :- https://updategadh.com/ 
# Developed By UPDATEGADH TEAM

from django import forms
from .models import Product, Supplier, Customer, Purchase, Sale, Expense, ReturnRecord

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name","sku","category","supplier","price","stock","reorder_level"]

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ["name","phone","email","address"]

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ["name","phone","email","address"]

class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ["supplier","product","quantity","unit_cost"]

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ["customer","product","quantity","unit_price"]

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ["category","description","amount"]

class ReturnForm(forms.ModelForm):
    class Meta:
        model = ReturnRecord
        fields = ["return_type","product","quantity","reason","status"]
