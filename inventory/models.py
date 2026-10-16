from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True


class Category(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=255, blank=True)
    def __str__(self):
        return self.name
    class Meta:
        ordering = ["name"]
        verbose_name_plural = "categories"


class Supplier(TimeStampedModel):
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    def __str__(self):
        return self.name
    class Meta:
        ordering = ["name"]


class Customer(TimeStampedModel):
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    def __str__(self):
        return self.name
    class Meta:
        ordering = ["name"]


class Product(TimeStampedModel):
    name = models.CharField(max_length=150)
    sku = models.CharField(max_length=50, unique=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="products")
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name="products")
    price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    cost_price = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    stock = models.PositiveIntegerField(default=0)
    reorder_level = models.PositiveIntegerField(default=5)
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return f"{self.name} ({self.sku})"
    @property
    def stock_value(self):
        return self.stock * self.cost_price
    @property
    def is_low_stock(self):
        return self.stock <= self.reorder_level
    class Meta:
        ordering = ["name"]


class Purchase(TimeStampedModel):
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name="purchases")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="purchases")
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_cost = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    reference = models.CharField(max_length=80, blank=True)
    notes = models.CharField(max_length=255, blank=True)
    purchased_at = models.DateTimeField(auto_now_add=True)
    @property
    def total(self):
        return self.quantity * self.unit_cost
    def __str__(self):
        return f"Purchase #{self.pk}: {self.product}"


class Sale(TimeStampedModel):
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, null=True, blank=True, related_name="sales")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="sales")
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    reference = models.CharField(max_length=80, blank=True)
    notes = models.CharField(max_length=255, blank=True)
    sold_at = models.DateTimeField(auto_now_add=True)
    @property
    def total(self):
        return self.quantity * self.unit_price
    def __str__(self):
        return f"Sale #{self.pk}: {self.product}"


class Expense(TimeStampedModel):
    category = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    spent_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.category}: {self.amount}"


class ReturnRecord(TimeStampedModel):
    RETURN_TYPES = [("SALE", "Customer return"), ("PURCHASE", "Return to supplier")]
    STATUS_CHOICES = [("APPROVED", "Approved"), ("PENDING", "Pending")]
    return_type = models.CharField(max_length=10, choices=RETURN_TYPES)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="returns")
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    reason = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="APPROVED")
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.get_return_type_display()} #{self.pk}"


class StockMovement(models.Model):
    MOVEMENT_TYPES = [("OPENING", "Opening balance"), ("PURCHASE", "Purchase"), ("SALE", "Sale"),
                      ("SALE_RETURN", "Customer return"), ("SUPPLIER_RETURN", "Supplier return"),
                      ("ADJUSTMENT", "Manual adjustment")]
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="movements")
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    quantity_change = models.IntegerField()
    balance_after = models.PositiveIntegerField()
    note = models.CharField(max_length=255, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["-created_at"]
    def __str__(self):
        return f"{self.product.sku}: {self.quantity_change:+d}"
