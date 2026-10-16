import csv
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import F, Q, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from .forms import CategoryForm, CustomerForm, ExpenseForm, ProductForm, PurchaseForm, ReturnForm, SaleForm, SupplierForm
from .models import Category, Customer, Expense, Product, Purchase, ReturnRecord, Sale, StockMovement, Supplier

def list_context(request, queryset, kind, title, searchable=False):
    query = request.GET.get("q", "").strip()
    if searchable and query:
        if kind == "products":
            queryset = queryset.filter(Q(name__icontains=query) | Q(sku__icontains=query))
        elif kind == "categories":
            queryset = queryset.filter(Q(name__icontains=query) | Q(description__icontains=query))
        elif kind in ("suppliers", "customers"):
            queryset = queryset.filter(Q(name__icontains=query) | Q(phone__icontains=query) | Q(email__icontains=query))
    page_obj = Paginator(queryset, 20).get_page(request.GET.get("page"))
    return render(request, "list.html", {"title": title, "kind": kind, "items": page_obj.object_list,
                                         "page_obj": page_obj, "q": query})

def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        user = authenticate(request, username=request.POST.get("username", "").strip(),
                            password=request.POST.get("password", ""))
        if user and user.is_active:
            login(request, user)
            return redirect(request.GET.get("next") or "dashboard")
        messages.error(request, "Username or password was incorrect.")
    return render(request, "login.html")

@login_required
def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect("login")
    return render(request, "confirm_logout.html")

@login_required
def dashboard(request):
    low_stock_products = Product.objects.filter(is_active=True, stock__lte=F("reorder_level")).order_by("stock")[:8]
    sales_total = sum((x.total for x in Sale.objects.select_related("product")), Decimal("0"))
    purchase_total = sum((x.total for x in Purchase.objects.select_related("product")), Decimal("0"))
    expense_total = Expense.objects.aggregate(v=Sum("amount"))["v"] or Decimal("0")
    return render(request, "dashboard.html", {
        "title": "Dashboard", "products_count": Product.objects.filter(is_active=True).count(),
        "suppliers_count": Supplier.objects.count(), "customers_count": Customer.objects.count(),
        "categories_count": Category.objects.count(), "low_stock": Product.objects.filter(is_active=True, stock__lte=F("reorder_level")).count(),
        "sales_qty": Sale.objects.aggregate(v=Sum("quantity"))["v"] or 0,
        "purchase_qty": Purchase.objects.aggregate(v=Sum("quantity"))["v"] or 0,
        "revenue": sales_total, "purchase_value": purchase_total, "expenses": expense_total,
        "recent_sales": Sale.objects.select_related("product", "customer").order_by("-sold_at")[:8],
        "low_stock_products": low_stock_products,
    })

@login_required
def products(request):
    return list_context(request, Product.objects.filter(is_active=True).select_related("category", "supplier").order_by("name"),
                        "products", "Products", True)

@login_required
def product_add(request):
    form = ProductForm(request.POST or None)
    if form.is_valid():
        product = form.save()
        StockMovement.objects.create(product=product, movement_type="OPENING", quantity_change=product.stock,
                                     balance_after=product.stock, note="Product created", created_by=request.user)
        messages.success(request, "Product created.")
        return redirect("products")
    return render(request, "form.html", {"title": "Add product", "form": form})

@login_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    old_stock = product.stock
    form = ProductForm(request.POST or None, instance=product)
    if form.is_valid():
        updated = form.save()
        delta = updated.stock - old_stock
        if delta:
            StockMovement.objects.create(product=updated, movement_type="ADJUSTMENT", quantity_change=delta,
                                         balance_after=updated.stock, note="Stock adjusted from product edit",
                                         created_by=request.user)
        messages.success(request, "Product updated.")
        return redirect("products")
    return render(request, "form.html", {"title": f"Edit {product.name}", "form": form})

@login_required
def product_delete(request, pk):
    if request.method != "POST":
        return redirect("products")
    if not (request.user.is_superuser or request.user.is_staff):
        messages.error(request, "Administrator permission is required.")
        return redirect("products")
    product = get_object_or_404(Product, pk=pk)
    product.is_active = False
    product.save(update_fields=["is_active", "updated_at"])
    messages.success(request, "Product archived. Transaction history was preserved.")
    return redirect("products")

@login_required
def categories(request):
    return list_context(request, Category.objects.all(), "categories", "Categories", True)

@login_required
def category_add(request):
    form = CategoryForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Category created.")
        return redirect("categories")
    return render(request, "form.html", {"title": "Add category", "form": form})

@login_required
def category_edit(request, pk):
    obj = get_object_or_404(Category, pk=pk)
    form = CategoryForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save()
        messages.success(request, "Category updated.")
        return redirect("categories")
    return render(request, "form.html", {"title": "Edit category", "form": form})

@login_required
def suppliers(request):
    return list_context(request, Supplier.objects.all(), "suppliers", "Suppliers", True)

@login_required
def supplier_add(request):
    form = SupplierForm(request.POST or None)
    if form.is_valid():
        form.save(); messages.success(request, "Supplier created."); return redirect("suppliers")
    return render(request, "form.html", {"title": "Add supplier", "form": form})

@login_required
def customers(request):
    return list_context(request, Customer.objects.all(), "customers", "Customers", True)

@login_required
def customer_add(request):
    form = CustomerForm(request.POST or None)
    if form.is_valid():
        form.save(); messages.success(request, "Customer created."); return redirect("customers")
    return render(request, "form.html", {"title": "Add customer", "form": form})

@login_required
@transaction.atomic
def purchase_add(request):
    form = PurchaseForm(request.POST or None)
    if form.is_valid():
        obj = form.save()
        product = Product.objects.select_for_update().get(pk=obj.product_id)
        product.stock += obj.quantity
        product.cost_price = obj.unit_cost
        product.save(update_fields=["stock", "cost_price", "updated_at"])
        StockMovement.objects.create(product=product, movement_type="PURCHASE", quantity_change=obj.quantity,
                                     balance_after=product.stock, note=f"Purchase #{obj.pk}", created_by=request.user)
        messages.success(request, f"Purchase saved. Stock for {product.name} increased by {obj.quantity}.")
        return redirect("purchases")
    return render(request, "form.html", {"title": "Record purchase", "form": form})

@login_required
def purchases(request):
    return list_context(request, Purchase.objects.select_related("supplier", "product").order_by("-purchased_at"),
                        "purchases", "Purchases")

@login_required
@transaction.atomic
def sale_add(request):
    form = SaleForm(request.POST or None)
    if form.is_valid():
        sale = form.save(commit=False)
        product = Product.objects.select_for_update().get(pk=sale.product_id)
        if sale.quantity > product.stock:
            form.add_error("quantity", f"Only {product.stock} unit(s) are available.")
        else:
            sale.save()
            product.stock -= sale.quantity
            product.save(update_fields=["stock", "updated_at"])
            StockMovement.objects.create(product=product, movement_type="SALE", quantity_change=-sale.quantity,
                                         balance_after=product.stock, note=f"Sale #{sale.pk}", created_by=request.user)
            messages.success(request, f"Sale saved. Stock for {product.name} decreased by {sale.quantity}.")
            return redirect("sales")
    return render(request, "form.html", {"title": "Record sale", "form": form})

@login_required
def sales(request):
    return list_context(request, Sale.objects.select_related("customer", "product").order_by("-sold_at"),
                        "sales", "Sales")

@login_required
def expenses(request):
    return list_context(request, Expense.objects.order_by("-spent_at"), "expenses", "Expenses")

@login_required
def expense_add(request):
    form = ExpenseForm(request.POST or None)
    if form.is_valid():
        form.save(); messages.success(request, "Expense recorded."); return redirect("expenses")
    return render(request, "form.html", {"title": "Add expense", "form": form})

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
                movement = "SALE_RETURN"
                change = record.quantity
            else:
                if record.quantity > product.stock:
                    form.add_error("quantity", f"Only {product.stock} unit(s) are available to return.")
                    return render(request, "form.html", {"title": "Record return", "form": form})
                product.stock -= record.quantity
                movement = "SUPPLIER_RETURN"
                change = -record.quantity
            product.save(update_fields=["stock", "updated_at"])
            record.save()
            StockMovement.objects.create(product=product, movement_type=movement, quantity_change=change,
                                         balance_after=product.stock, note=f"Return #{record.pk}", created_by=request.user)
        else:
            record.save()
        messages.success(request, "Return recorded.")
        return redirect("returns")
    return render(request, "form.html", {"title": "Record return", "form": form})

@login_required
def returns(request):
    return list_context(request, ReturnRecord.objects.select_related("product").order_by("-created_at"),
                        "returns", "Returns")

@login_required
def export_products_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="stockpilot-products.csv"'
    writer = csv.writer(response)
    writer.writerow(["Name", "SKU", "Category", "Supplier", "Selling Price", "Cost Price", "Stock", "Reorder Level", "Stock Value"])
    for p in Product.objects.filter(is_active=True).select_related("category", "supplier"):
        writer.writerow([p.name, p.sku, p.category or "", p.supplier or "", p.price, p.cost_price, p.stock,
                         p.reorder_level, p.stock_value])
    return response
