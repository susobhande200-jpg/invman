# StockPilot — Inventory & Small Business Operations

A Django web application for small shops and student project demonstrations. It brings product catalogue, stock levels, purchases, sales, supplier/customer records, expenses, returns, low-stock alerts, and CSV export into one responsive interface.

## Included features

- Modern responsive dashboard and login
- Products with SKU, category, supplier, selling price, cost price, stock and reorder threshold
- Product create/edit/archive; archived products preserve transaction history
- Categories with create/edit
- Supplier and customer directory
- Purchase entry increases product stock
- Sale entry checks available stock and decreases it
- Customer returns and supplier returns update stock when approved
- Stock movement ledger for opening stock, purchases, sales, returns and manual adjustments
- Low-stock warning list
- Search and pagination for main directories
- CSV export for product inventory
- Django admin at `/django-admin/`
- SQLite for local development; PostgreSQL support using `DATABASE_URL`
- WhiteNoise static assets for deployment

## Local installation (Windows)

1. Extract this ZIP.
2. Open the extracted `stockpilot_inventory` folder in VS Code.
3. Open Terminal in that folder (the folder containing `manage.py`).
4. Run:

```powershell
py -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python manage.py check
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

5. Open `http://127.0.0.1:8000/` and sign in with the superuser you created.

## Deploy to Render

1. Create a GitHub repository and upload the contents of this folder.
2. Create a Render PostgreSQL database and copy its **Internal Database URL** if the web service and database are in the same Render region.
3. Create a Render Web Service connected to that repository.
4. Use:
   - Build command: `pip install -r requirements.txt && python manage.py migrate --noinput && python manage.py collectstatic --noinput`
   - Start command: `gunicorn stockpilot.wsgi:application`
5. Configure environment variables:
   - `DJANGO_SECRET_KEY`: a long random secret
   - `DJANGO_DEBUG`: `False`
   - `DJANGO_ALLOWED_HOSTS`: your deployed hostname, e.g. `stockpilot-example.onrender.com`
   - `DATABASE_URL`: the PostgreSQL connection URL
6. Deploy, then create the first user with a one-time management action or locally before deployment. Do not commit passwords or secret keys.

`render.yaml` is provided as a starting point; the `DATABASE_URL` value must be configured in Render. The free Render web service filesystem is ephemeral, so use PostgreSQL for records you want to keep.

## Important notes

- This ZIP is a new project with a new Django app label and new database schema. It is **not a drop-in patch** for the older `invman` database. Back up/export old data before migrating any records.
- The application is a strong project foundation, but test workflows and permissions before using it for real business operations.
- Sales and purchase totals are simple recorded transaction totals; tax, discounts, payments, accounting reconciliation, and invoice numbering are not implemented.
