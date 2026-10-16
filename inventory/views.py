from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import F, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render

from .forms import (
    CategoryForm, CustomerForm, ExpenseForm, ProductForm, PurchaseForm,
    ReturnForm, SaleForm, SupplierForm,
)
from .models import Category, Customer, Expense, Product, Purchase, ReturnRecord, Sale, Supplier


def is_admin(user):
    return user.is_superuser or user.is_staff


def render_list(request, *, title, queryset, kind, searchable=False):
    query = request.GET.get("q", "").strip()
    if searchable and query:
        if kind == "products":
            queryset = queryset.filter(Q(name__icontains=query) | Q(sku__icontains=query))
        elif kind == "categories":
            queryset = queryset.filter(name__icontains=query)
        elif kind in {"suppliers", "customers"}:
            queryset = queryset.filter(
                Q(name__icontains=query) | Q(phone__icontains=query) | Q(email__icontains=query)
            )
    paginator = Paginator(queryset, 20)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "list.html", {
        "title": title, "items": page_obj.object_list, "kind": kind,
        "q": query, "page_obj": page_obj,
    })


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect(request.GET.get("next") or "dashboard")
        messages.error(request, "Invalid username or password.")
    return render(request, "login.html")


@login_required
def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect("login")
    return render(request, "confirm_logout.html")


@login_required
def dashboard(request):
    low_stock = Product.objects.filter(stock__lte=F("reorder_level")).count()
    sales_qty = Sale.objects.aggregate(v=Sum("quantity"))["v"] or 0
    purchase_qty = Purchase.objects.aggregate(v=Sum("quantity"))["v"] or 0
    revenue = sum((sale.total for sale in Sale.objects.select_related("product")), Decimal("0"))
    expenses_total = Expense.objects.aggregate(v=Sum("amount"))["v"] or Decimal("0")
    context = {
        "title": "Dashboard",
        "products_count": Product.objects.count(),
        "suppliers_count": Supplier.objects.count(),
        "customers_count": Customer.objects.count(),
        "categories_count": Category.objects.count(),
        "low_stock": low_stock,
        "sales_qty": sales_qty,
        "purchase_qty": purchase_qty,
        "revenue": revenue,
        "expenses": expenses_total,
        "recent_sales": Sale.objects.select_related("product", "customer").order_by("-sold_at")[:8],
        "low_stock_products": Product.objects.filter(stock__lte=F("reorder_level")).order_by("stock")[:8],
    }
    return render(request, "dashboard.html", context)


@login_required
def products(request):
    return render_list(
        request, title="Products",
        queryset=Product.objects.select_related("category", "supplier").order_by("name"),
        kind="products", searchable=True,
    )


@login_required
def product_add(request):
    form = ProductForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Product saved successfully.")
        return redirect("products")
    return render(request, "form.html", {"title": "Add Product", "form": form})


@login_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, instance=product)
    if form.is_valid():
        form.save()
        messages.success(request, "Product updated successfully.")
        return redirect("products")
    return render(request, "form.html", {"title": f"Edit {product.name}", "form": form})


@login_required
def product_delete(request, pk):
    if request.method != "POST":
        messages.error(request, "Please submit the delete form to remove a product.")
        return redirect("products")
    if not is_admin(request.user):
        messages.error(request, "Only an administrator can delete products.")
        return redirect("products")
    product = get_object_or_404(Product, pk=pk)
    try:
        product.delete()
        messages.success(request, "Product deleted.")
    except Exception:
        messages.error(request, "This product cannot be deleted because it is linked to existing transactions.")
    return redirect("products")


@login_required
def categories(request):
    return render_list(
        request, title="Categories",
        queryset=Category.objects.order_by("name"), kind="categories", searchable=True,
    )


@login_required
def category_add(request):
    form = CategoryForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Category created. You can now assign it to products.")
        return redirect("categories")
    return render(request, "form.html", {"title": "Add Category", "form": form})


@login_required
def suppliers(request):
    return render_list(request, title="Suppliers", queryset=Supplier.objects.order_by("name"),
                       kind="suppliers", searchable=True)


@login_required
def supplier_add(request):
    form = SupplierForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Supplier saved.")
        return redirect("suppliers")
    return render(request, "form.html", {"title": "Add Supplier", "form": form})


@login_required
def customers(request):
    return render_list(request, title="Customers", queryset=Customer.objects.order_by("name"),
                       kind="customers", searchable=True)


@login_required
def customer_add(request):
    form = CustomerForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Customer saved.")
        return redirect("customers")
    return render(request, "form.html", {"title": "Add Customer", "form": form})


@login_required
def purchases(request):
    return render_list(request, title="Purchases",
                       queryset=Purchase.objects.select_related("supplier", "product").order_by("-purchased_at"),
                       kind="purchases")


@login_required
@transaction.atomic
def purchase_add(request):
    form = PurchaseForm(request.POST or None)
    if form.is_valid():
        purchase = form.save()
        Product.objects.filter(pk=purchase.product_id).update(stock=F("stock") + purchase.quantity)
        messages.success(request, "Purchase recorded and stock increased.")
        return redirect("purchases")
    return render(request, "form.html", {"title": "Record Purchase", "form": form})


@login_required
def sales(request):
    return render_list(request, title="Sales",
                       queryset=Sale.objects.select_related("customer", "product").order_by("-sold_at"),
                       kind="sales")


@login_required
@transaction.atomic
def sale_add(request):
    form = SaleForm(request.POST or None)
    if form.is_valid():
        sale = form.save(commit=False)
        product = Product.objects.select_for_update().get(pk=sale.product_id)
        if sale.quantity > product.stock:
            form.add_error("quantity", f"Only {product.stock} unit(s) are currently in stock.")
        else:
            sale.save()
            Product.objects.filter(pk=product.pk).update(stock=F("stock") - sale.quantity)
            messages.success(request, "Sale recorded and stock reduced.")
            return redirect("sales")
    return render(request, "form.html", {"title": "Record Sale", "form": form})


@login_required
def expenses(request):
    return render_list(request, title="Expenses", queryset=Expense.objects.order_by("-spent_at"),
                       kind="expenses")


@login_required
def expense_add(request):
    form = ExpenseForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Expense recorded.")
        return redirect("expenses")
    return render(request, "form.html", {"title": "Add Expense", "form": form})


@login_required
def returns(request):
    return render_list(request, title="Returns",
                       queryset=ReturnRecord.objects.select_related("product").order_by("-created_at"),
                       kind="returns")


@login_required
@transaction.atomic
def return_add(request):
    form = ReturnForm(request.POST or None)
    if form.is_valid():
        record = form.save(commit=False)
        product = Product.objects.select_for_update().get(pk=record.product_id)
        if record.status == "APPROVED":
            if record.return_type == "SALE":
                product.stock += record.quantity
            else:
                if record.quantity > product.stock:
                    form.add_error("quantity", f"Only {product.stock} unit(s) are available to return to supplier.")
                    return render(request, "form.html", {"title": "Add Return", "form": form})
                product.stock -= record.quantity
            product.save(update_fields=["stock"])
        record.save()
        messages.success(request, "Return recorded.")
        return redirect("returns")
    return render(request, "form.html", {"title": "Add Return", "form": form})
