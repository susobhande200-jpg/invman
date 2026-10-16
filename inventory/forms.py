from django import forms
from .models import Category, Customer, Expense, Product, Purchase, ReturnRecord, Sale, Supplier

class StyledModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs.setdefault("class", "input-control")
            if isinstance(field.widget, forms.Select):
                field.widget.attrs["class"] += " select-control"

class ProductForm(StyledModelForm):
    class Meta:
        model = Product
        fields = ["name", "sku", "category", "supplier", "price", "cost_price", "stock", "reorder_level", "is_active"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "e.g. Wireless keyboard"}),
            "sku": forms.TextInput(attrs={"placeholder": "e.g. KEY-001"}),
            "price": forms.NumberInput(attrs={"min": "0", "step": "0.01"}),
            "cost_price": forms.NumberInput(attrs={"min": "0", "step": "0.01"}),
            "stock": forms.NumberInput(attrs={"min": "0", "step": "1"}),
            "reorder_level": forms.NumberInput(attrs={"min": "0", "step": "1"}),
        }
    def clean_sku(self):
        return self.cleaned_data["sku"].strip().upper()

class CategoryForm(StyledModelForm):
    class Meta:
        model = Category
        fields = ["name", "description"]
        widgets = {"name": forms.TextInput(attrs={"placeholder": "e.g. Electronics"}),
                   "description": forms.TextInput(attrs={"placeholder": "Optional description"})}

class SupplierForm(StyledModelForm):
    class Meta:
        model = Supplier
        fields = ["name", "phone", "email", "address"]
        widgets = {"name": forms.TextInput(attrs={"placeholder": "Supplier company"}),
                   "phone": forms.TextInput(attrs={"placeholder": "Phone"}),
                   "address": forms.Textarea(attrs={"rows": 3})}

class CustomerForm(StyledModelForm):
    class Meta:
        model = Customer
        fields = ["name", "phone", "email", "address"]
        widgets = {"name": forms.TextInput(attrs={"placeholder": "Customer name"}),
                   "phone": forms.TextInput(attrs={"placeholder": "Phone"}),
                   "address": forms.Textarea(attrs={"rows": 3})}

class PurchaseForm(StyledModelForm):
    class Meta:
        model = Purchase
        fields = ["supplier", "product", "quantity", "unit_cost", "reference", "notes"]
        widgets = {"quantity": forms.NumberInput(attrs={"min": "1", "step": "1"}),
                   "unit_cost": forms.NumberInput(attrs={"min": "0", "step": "0.01"})}

class SaleForm(StyledModelForm):
    class Meta:
        model = Sale
        fields = ["customer", "product", "quantity", "unit_price", "reference", "notes"]
        widgets = {"quantity": forms.NumberInput(attrs={"min": "1", "step": "1"}),
                   "unit_price": forms.NumberInput(attrs={"min": "0", "step": "0.01"})}

class ExpenseForm(StyledModelForm):
    class Meta:
        model = Expense
        fields = ["category", "description", "amount"]
        widgets = {"category": forms.TextInput(attrs={"placeholder": "e.g. Transport"}),
                   "description": forms.TextInput(attrs={"placeholder": "What was this expense for?"}),
                   "amount": forms.NumberInput(attrs={"min": "0", "step": "0.01"})}

class ReturnForm(StyledModelForm):
    class Meta:
        model = ReturnRecord
        fields = ["return_type", "product", "quantity", "reason", "status"]
        widgets = {"quantity": forms.NumberInput(attrs={"min": "1", "step": "1"})}
