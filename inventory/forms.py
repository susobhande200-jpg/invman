from django import forms
from .models import (
    Category, Customer, Expense, Product, Purchase, ReturnRecord, Sale, Supplier,
)


class StyledModelForm(forms.ModelForm):
    """Apply consistent accessible CSS classes to all generated form controls."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = (existing + " input-control").strip()
            field.widget.attrs.setdefault("autocomplete", "off")


class ProductForm(StyledModelForm):
    class Meta:
        model = Product
        fields = ["name", "sku", "category", "supplier", "price", "stock", "reorder_level"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "e.g. HP Laptop"}),
            "sku": forms.TextInput(attrs={"placeholder": "e.g. LAP-001"}),
            "price": forms.NumberInput(attrs={"min": "0", "step": "0.01"}),
            "stock": forms.NumberInput(attrs={"min": "0", "step": "1"}),
            "reorder_level": forms.NumberInput(attrs={"min": "0", "step": "1"}),
        }

    def clean_sku(self):
        return self.cleaned_data["sku"].strip().upper()

    def clean_price(self):
        price = self.cleaned_data["price"]
        if price < 0:
            raise forms.ValidationError("Price cannot be negative.")
        return price


class CategoryForm(StyledModelForm):
    class Meta:
        model = Category
        fields = ["name"]
        widgets = {"name": forms.TextInput(attrs={"placeholder": "e.g. Electronics"})}

    def clean_name(self):
        return self.cleaned_data["name"].strip()


class SupplierForm(StyledModelForm):
    class Meta:
        model = Supplier
        fields = ["name", "phone", "email", "address"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Supplier or company name"}),
            "phone": forms.TextInput(attrs={"placeholder": "Phone number"}),
            "address": forms.Textarea(attrs={"rows": 3}),
        }


class CustomerForm(StyledModelForm):
    class Meta:
        model = Customer
        fields = ["name", "phone", "email", "address"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Customer name"}),
            "phone": forms.TextInput(attrs={"placeholder": "Phone number"}),
            "address": forms.Textarea(attrs={"rows": 3}),
        }


class PurchaseForm(StyledModelForm):
    class Meta:
        model = Purchase
        fields = ["supplier", "product", "quantity", "unit_cost"]
        widgets = {
            "quantity": forms.NumberInput(attrs={"min": "1", "step": "1"}),
            "unit_cost": forms.NumberInput(attrs={"min": "0", "step": "0.01"}),
        }

    def clean_quantity(self):
        quantity = self.cleaned_data["quantity"]
        if quantity < 1:
            raise forms.ValidationError("Quantity must be at least 1.")
        return quantity


class SaleForm(StyledModelForm):
    class Meta:
        model = Sale
        fields = ["customer", "product", "quantity", "unit_price"]
        widgets = {
            "quantity": forms.NumberInput(attrs={"min": "1", "step": "1"}),
            "unit_price": forms.NumberInput(attrs={"min": "0", "step": "0.01"}),
        }

    def clean_quantity(self):
        quantity = self.cleaned_data["quantity"]
        if quantity < 1:
            raise forms.ValidationError("Quantity must be at least 1.")
        return quantity


class ExpenseForm(StyledModelForm):
    class Meta:
        model = Expense
        fields = ["category", "description", "amount"]
        widgets = {
            "category": forms.TextInput(attrs={"placeholder": "e.g. Transport"}),
            "description": forms.TextInput(attrs={"placeholder": "What was the expense for?"}),
            "amount": forms.NumberInput(attrs={"min": "0", "step": "0.01"}),
        }


class ReturnForm(StyledModelForm):
    class Meta:
        model = ReturnRecord
        fields = ["return_type", "product", "quantity", "reason", "status"]
        widgets = {
            "quantity": forms.NumberInput(attrs={"min": "1", "step": "1"}),
            "reason": forms.TextInput(attrs={"placeholder": "Reason for return"}),
        }

    def clean_quantity(self):
        quantity = self.cleaned_data["quantity"]
        if quantity < 1:
            raise forms.ValidationError("Quantity must be at least 1.")
        return quantity
