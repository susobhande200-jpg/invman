# FOR MORE REAL TIME PROJECTS VISIT :- https://updategadh.com/ 
# Developed By UPDATEGADH TEAM

from decimal import Decimal
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F, Sum
from django.shortcuts import get_object_or_404, redirect, render
from .forms import ProductForm, SupplierForm, CustomerForm, PurchaseForm, SaleForm, ExpenseForm, ReturnForm
from .models import Product, Supplier, Customer, Purchase, Sale, Expense, ReturnRecord, Category

def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        user = authenticate(request, username=request.POST.get("username"), password=request.POST.get("password"))
        if user:
            login(request, user)
            return redirect("dashboard")
        messages.error(request, "Invalid username or password.")
    return render(request, "login.html")

@login_required
def logout_view(request):
    logout(request)
    return redirect("login")

@login_required
def dashboard(request):
    low_stock = Product.objects.filter(stock__lte=F("reorder_level")).count()
    sales_total = Sale.objects.aggregate(v=Sum("quantity"))["v"] or 0
    purchase_total = Purchase.objects.aggregate(v=Sum("quantity"))["v"] or 0
    revenue = sum((s.total for s in Sale.objects.all()), Decimal("0"))
    expenses = Expense.objects.aggregate(v=Sum("amount"))["v"] or Decimal("0")
    role = getattr(getattr(request.user, "profile", None), "role", "STAFF")
    return render(request, "dashboard.html", {
        "role": role, "products_count": Product.objects.count(), "suppliers_count": Supplier.objects.count(),
        "customers_count": Customer.objects.count(), "low_stock": low_stock,
        "sales_qty": sales_total, "purchase_qty": purchase_total,
        "revenue": revenue, "expenses": expenses,
        "recent_sales": Sale.objects.select_related("product","customer").order_by("-sold_at")[:6],
    })

@login_required
def products(request):
    q = request.GET.get("q","").strip()
    qs = Product.objects.select_related("category","supplier").order_by("name")
    if q: qs = qs.filter(name__icontains=q) | qs.filter(sku__icontains=q)
    return render(request, "list.html", {"title":"Products","items":qs,"kind":"products","q":q})

@login_required
def product_add(request):
    form = ProductForm(request.POST or None)
    if form.is_valid():
        form.save(); messages.success(request,"Product saved."); return redirect("products")
    return render(request,"form.html",{"title":"Add Product","form":form})

@login_required
def product_delete(request, pk):
    role = getattr(getattr(request.user, "profile", None), "role", "STAFF")
    if request.method == "POST" and role == "ADMIN":
        get_object_or_404(Product,pk=pk).delete()
        messages.success(request,"Product deleted.")
    return redirect("products")

@login_required
def suppliers(request):
    return render(request,"list.html",{"title":"Suppliers","items":Supplier.objects.order_by("name"),"kind":"suppliers"})

@login_required
def supplier_add(request):
    form=SupplierForm(request.POST or None)
    if form.is_valid(): form.save(); messages.success(request,"Supplier saved."); return redirect("suppliers")
    return render(request,"form.html",{"title":"Add Supplier","form":form})

@login_required
def customers(request):
    return render(request,"list.html",{"title":"Customers","items":Customer.objects.order_by("name"),"kind":"customers"})

@login_required
def customer_add(request):
    form=CustomerForm(request.POST or None)
    if form.is_valid(): form.save(); messages.success(request,"Customer saved."); return redirect("customers")
    return render(request,"form.html",{"title":"Add Customer","form":form})

@login_required
@transaction.atomic
def purchases(request):
    return render(request,"list.html",{"title":"Purchases","items":Purchase.objects.select_related("supplier","product").order_by("-purchased_at"),"kind":"purchases"})

@login_required
@transaction.atomic
def purchase_add(request):
    form=PurchaseForm(request.POST or None)
    if form.is_valid():
        obj=form.save()
        Product.objects.filter(pk=obj.product_id).update(stock=F("stock")+obj.quantity)
        messages.success(request,"Purchase recorded and stock increased.")
        return redirect("purchases")
    return render(request,"form.html",{"title":"Record Purchase","form":form})

@login_required
def sales(request):
    return render(request,"list.html",{"title":"Sales","items":Sale.objects.select_related("customer","product").order_by("-sold_at"),"kind":"sales"})

@login_required
@transaction.atomic
def sale_add(request):
    form=SaleForm(request.POST or None)
    if form.is_valid():
        obj=form.save(commit=False)
        if obj.quantity > obj.product.stock:
            form.add_error("quantity","Insufficient stock available.")
        else:
            obj.save()
            Product.objects.filter(pk=obj.product_id).update(stock=F("stock")-obj.quantity)
            messages.success(request,"Sale recorded and stock reduced.")
            return redirect("sales")
    return render(request,"form.html",{"title":"Record Sale","form":form})

@login_required
def expenses(request):
    return render(request,"list.html",{"title":"Expenses","items":Expense.objects.order_by("-spent_at"),"kind":"expenses"})

@login_required
def expense_add(request):
    form=ExpenseForm(request.POST or None)
    if form.is_valid(): form.save(); messages.success(request,"Expense recorded."); return redirect("expenses")
    return render(request,"form.html",{"title":"Add Expense","form":form})

@login_required
@transaction.atomic
def returns(request):
    return render(request,"list.html",{"title":"Returns","items":ReturnRecord.objects.select_related("product").order_by("-created_at"),"kind":"returns"})

@login_required
@transaction.atomic
def return_add(request):
    form=ReturnForm(request.POST or None)
    if form.is_valid():
        obj=form.save()
        if obj.status == "APPROVED":
            if obj.return_type == "SALE":
                Product.objects.filter(pk=obj.product_id).update(stock=F("stock")+obj.quantity)
            else:
                Product.objects.filter(pk=obj.product_id).update(stock=F("stock")-obj.quantity)
        messages.success(request,"Return recorded.")
        return redirect("returns")
    return render(request,"form.html",{"title":"Add Return","form":form})
