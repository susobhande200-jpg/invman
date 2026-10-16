# Initial schema for a fresh StockPilot installation.
import django.core.validators
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(name="Category", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("created_at", models.DateTimeField(auto_now_add=True)), ("updated_at", models.DateTimeField(auto_now=True)),
            ("name", models.CharField(max_length=100, unique=True)), ("description", models.CharField(blank=True, max_length=255)),
        ], options={"ordering": ["name"], "verbose_name_plural": "categories"}),
        migrations.CreateModel(name="Customer", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("created_at", models.DateTimeField(auto_now_add=True)), ("updated_at", models.DateTimeField(auto_now=True)),
            ("name", models.CharField(max_length=150)), ("phone", models.CharField(blank=True, max_length=30)),
            ("email", models.EmailField(blank=True, max_length=254)), ("address", models.TextField(blank=True)),
        ], options={"ordering": ["name"]}),
        migrations.CreateModel(name="Expense", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("created_at", models.DateTimeField(auto_now_add=True)), ("updated_at", models.DateTimeField(auto_now=True)),
            ("category", models.CharField(max_length=100)), ("description", models.CharField(max_length=255)),
            ("amount", models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(0)])),
            ("spent_at", models.DateTimeField(auto_now_add=True)),
        ]),
        migrations.CreateModel(name="Product", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("created_at", models.DateTimeField(auto_now_add=True)), ("updated_at", models.DateTimeField(auto_now=True)),
            ("name", models.CharField(max_length=150)), ("sku", models.CharField(max_length=50, unique=True)),
            ("price", models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(0)])),
            ("cost_price", models.DecimalField(decimal_places=2, default=0, max_digits=12, validators=[django.core.validators.MinValueValidator(0)])),
            ("stock", models.PositiveIntegerField(default=0)), ("reorder_level", models.PositiveIntegerField(default=5)),
            ("is_active", models.BooleanField(default=True)),
            ("category", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="products", to="inventory.category")),
        ], options={"ordering": ["name"]}),
        migrations.CreateModel(name="Supplier", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("created_at", models.DateTimeField(auto_now_add=True)), ("updated_at", models.DateTimeField(auto_now=True)),
            ("name", models.CharField(max_length=150)), ("phone", models.CharField(blank=True, max_length=30)),
            ("email", models.EmailField(blank=True, max_length=254)), ("address", models.TextField(blank=True)),
        ], options={"ordering": ["name"]}),
        migrations.AddField(model_name="product", name="supplier", field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="products", to="inventory.supplier")),
        migrations.CreateModel(name="Purchase", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("created_at", models.DateTimeField(auto_now_add=True)), ("updated_at", models.DateTimeField(auto_now=True)),
            ("quantity", models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)])),
            ("unit_cost", models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(0)])),
            ("reference", models.CharField(blank=True, max_length=80)), ("notes", models.CharField(blank=True, max_length=255)),
            ("purchased_at", models.DateTimeField(auto_now_add=True)),
            ("product", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="purchases", to="inventory.product")),
            ("supplier", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="purchases", to="inventory.supplier")),
        ]),
        migrations.CreateModel(name="Sale", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("created_at", models.DateTimeField(auto_now_add=True)), ("updated_at", models.DateTimeField(auto_now=True)),
            ("quantity", models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)])),
            ("unit_price", models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(0)])),
            ("reference", models.CharField(blank=True, max_length=80)), ("notes", models.CharField(blank=True, max_length=255)),
            ("sold_at", models.DateTimeField(auto_now_add=True)),
            ("customer", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="sales", to="inventory.customer")),
            ("product", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="sales", to="inventory.product")),
        ]),
        migrations.CreateModel(name="ReturnRecord", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("created_at", models.DateTimeField(auto_now_add=True)),
            ("return_type", models.CharField(choices=[("SALE", "Customer return"), ("PURCHASE", "Return to supplier")], max_length=10)),
            ("quantity", models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)])),
            ("reason", models.CharField(max_length=255)),
            ("status", models.CharField(choices=[("APPROVED", "Approved"), ("PENDING", "Pending")], default="APPROVED", max_length=20)),
            ("product", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="returns", to="inventory.product")),
        ]),
        migrations.CreateModel(name="StockMovement", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("movement_type", models.CharField(choices=[("OPENING", "Opening balance"), ("PURCHASE", "Purchase"), ("SALE", "Sale"), ("SALE_RETURN", "Customer return"), ("SUPPLIER_RETURN", "Supplier return"), ("ADJUSTMENT", "Manual adjustment")], max_length=20)),
            ("quantity_change", models.IntegerField()), ("balance_after", models.PositiveIntegerField()),
            ("note", models.CharField(blank=True, max_length=255)), ("created_at", models.DateTimeField(auto_now_add=True)),
            ("created_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ("product", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="movements", to="inventory.product")),
        ], options={"ordering": ["-created_at"]}),
    ]
