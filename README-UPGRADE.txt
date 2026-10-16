STOCKFLOW UPGRADE PATCH
=======================

This is a set of replacement files based on the code you shared. It is not a complete Django project ZIP; copy the files into the matching locations in your existing project.

BEFORE YOU CHANGE ANYTHING
--------------------------
1. Make a backup copy of your current project folder.
2. Do not delete db.sqlite3 or your migrations folder.
3. Never upload .env files, passwords, or secret keys to GitHub.
4. These files were prepared from the code and templates you shared; test locally before deploying.

WHAT THIS PATCH CHANGES
-----------------------
- Removes the Updategadh promotional comments from the supplied files.
- Adds a Categories page so categories can be created before adding products.
- Adds product editing and safer POST-only product deletion.
- Adds list pagination and search for products/categories/suppliers/customers.
- Improves form layout, responsive styling, error messages, and dashboard low-stock display.
- Uses is_superuser/is_staff for admin UI permissions rather than requiring every user to have a Profile row.
- Adds an optional ensure_admin management command that creates an admin only if it does not already exist.
- Adds Django admin URL at /django-admin/.
- Sets DEBUG off by default and enables WhiteNoise static file handling.

COPY FILES TO THESE LOCATIONS
-----------------------------
inventory_project/settings.py
inventory_project/urls.py
inventory/forms.py
inventory/models.py
inventory/views.py
templates/base.html
templates/dashboard.html
templates/form.html
templates/list.html
templates/login.html
templates/confirm_logout.html  (new file)
static/css/style.css
requirements.txt
inventory/management/__init__.py (new)
inventory/management/commands/__init__.py (new)
inventory/management/commands/ensure_admin.py (new)

LOCAL TESTING
-------------
Open a terminal in the folder that contains manage.py, then run:

    python -m pip install -r requirements.txt
    python manage.py check
    python manage.py migrate
    python manage.py runserver

Open http://127.0.0.1:8000/ and sign in with an existing user.
If you need to create a local administrator, run:

    python manage.py createsuperuser

RENDER
------
Do not paste your actual password into code or GitHub.

In Render > your service > Environment, add:
- DJANGO_SECRET_KEY = a long random secret
- DJANGO_DEBUG = False
- DJANGO_ALLOWED_HOSTS = invman-txpd.onrender.com
- DJANGO_SUPERUSER_USERNAME = your chosen username
- DJANGO_SUPERUSER_EMAIL = your email
- DJANGO_SUPERUSER_PASSWORD = a strong password

A possible Build Command is:

    pip install -r requirements.txt && python manage.py migrate --noinput && python manage.py ensure_admin && python manage.py collectstatic --noinput

This runs migrations during build and attempts to create an admin only if it does not exist. The SQLite database is still ephemeral on Render unless persistent storage is configured; for durable business data, configure PostgreSQL before relying on the live app. Do not assume this build-time SQLite approach is a permanent database solution.

IMPORTANT DATABASE NOTES
------------------------
The models in this patch retain the fields from the models you supplied to avoid intentional schema changes. Existing migrations are still required. If `python manage.py migrate` reports errors, stop and inspect the error before making further changes.
