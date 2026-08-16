# migrations and base-line migration

A migration is a Python file that acts like version control for your database. Instead of writing raw SQL commands by hand (like `CREATE TABLE`), Django reads your Python code, generates these migration files, and uses them to automatically build or update your database tables.

A **baseline migration** (often called the _initial migration_) is the very first set of migrations run on a brand-new project to set up Django's built-in core infrastructure.

Here is the exact breakdown of how they work and why you need them

---

### What is a Baseline Migration?

When you create a brand-new Django project, you haven't written any custom code or models yet. However, Django comes pre-packaged with several essential built-in features that require database tables to function:

- **Authentication (`auth`):** Tables to store your users, passwords, and permissions.
- **Admin (`admin`):** Tables to log actions taken in the backend admin panel.
- **Sessions (`sessions`):** Tables to keep users logged into your website.
- **Content Types (`contenttypes`):** A high-level system tracking all models in your app.

When you run your very first migration command right after creating a project:

```bash
uv run python manage.py migrate
```

You are executing the **baseline migrations**. Django looks into its own internal source code, finds the setup blueprints for these core systems, and creates roughly 10 to 15 default tables in your database.

If you do not run this baseline migration first, Django will crash the moment you try to log into the admin panel or create a user.

---

### Custom Migrations: The Two-Step Cycle

Once your baseline is established, you will write your own custom Python features. Every time you create or change a database table, you follow a strict two-step loop using `uv`:

#### Step 1: `makemigrations` (Drafting the Blueprint)

When you change your Python models, run this command. Django scans your code and drafts a new, numbered Python file inside your app's `migrations/` folder (e.g., `0001_initial.py`). It **does not** touch the database yet.

```bash
uv run python manage.py makemigrations
```

- **Analogy:** This is like drafting an architectural blueprint for an extension on a house. You have planned it out on paper, but no construction has started.

#### Step 2: `migrate` (Executing the Blueprint)

Run this command to execute the file. Django reads your new migration file, translates it into the correct SQL dialect (whether you use SQLite, PostgreSQL, or MySQL), and applies it directly to the database.

```bash
uv run python manage.py migrate
```

- **Analogy:** This is the construction phase. Workers read the blueprint and actually build the walls. Your database tables are now modified.

---

### Why this System is Powerful

1. **Team Sync:** When a teammate adds a new column to a table, they save the migration file to Git. When you pull their code, you simply run `uv run python manage.py migrate`, and your database instantly matches theirs.
2. **Safe Production Deploys:** You never have to manually run risky SQL queries on your live production server. The server runs the migration files automatically during deployment, keeping your data safe.
3. **Database Independence:** You write Python code once. If you use **SQLite** on your laptop for testing but deploy to **PostgreSQL** in production, Django translates the migrations perfectly for both systems automatically.

---

## Question? I haven't done baseline migrations .when i going to `/admin` path its showing me to login in with `username` and `password`. I haven't configured any `user name` or `password`. django hasn't asked me to define those during project setup?

When you create a new Django project, the database tables do not exist until you run the **baseline migrations**. Because those tables are missing, you cannot create a user yet, and trying to log in will result in an error.

Here is how to set up your database, create your admin login, and fix this issue using `uv`.

### 1. Run Baseline Migrations

You must create the default database tables for Django's authentication system to work. Run this command in your terminal:

```bash
uv run python manage.py migrate
```

### 2. Create Your Admin User

Django does not create a default username or password automatically. You must manually generate a superuser account by running:

```bash
uv run python manage.py createsuperuser
```

Follow the terminal prompts to enter your desired:

- Username
- Email address (optional)
- Password

### 3. Start the Server and Log In

Now that the database is ready and your account is created, start your development server:

```bash
uv run python manage.py runserver
```

Navigate back to `<http://localhost/admin>` and log in using the credentials you just created.

---

## Question? why its showing login window and where is the code for showing login window?\*\*

It shows the login window because **Django's routing works independently of your database state**.

Here is exactly why this happens in three simple steps:

### 1. The Route is Registered

When you created the project, Django automatically added the `/admin/` URL path to your `urls.py` file. Because that code exists, the URL is active and valid.

### 2. The View Only Code is Loaded

When you visit `/admin/`, Django runs the `admin login view code`. This code simply generates the HTML for the login form and sends it to your browser. It does not check if the database has tables or users until you actually click the "Log In" button.

### 3. The Error Happens After Submission

If you try to type a **random** username and click log in right now, the system will finally attempt to read the database. Because the tables do not exist yet, Django will crash and show you an operational error like `no such table: auth_user.`

---

## Question? where is template code because its not present in files and dir created by `uv run django-admin startproject mysite .`?

The code for the login window is located inside **Django's internal source code**, hidden deep within your environment's `site-packages` directory.

Because you are using `uv`, this code is managed inside a virtual environment. Here is exactly where the template, the view, and the route live:

### 1. The HTML Template

The actual visual layout of the login box is an HTML file named `login.html`. You can find it at this relative path inside your virtual environment's Python packages:

```text
.venv/lib/python3.x/site-packages/django/contrib/admin/templates/admin/login.html
```

### 2. The View Logic

The backend Python code that handles showing that form and processing the credentials lives inside the admin application's views file:

```text
.venv/lib/python3.x/site-packages/django/contrib/admin/sites.py
```

_(Look inside this file for the `login` method of the `AdminSite` class)._

### 3. The URL Route

In your own project, the entry point that links to this hidden code is in your main project folder's `urls.py` file. It looks like this:

```python
from django.contrib import admin
from django.urls import path
urlpatterns = [
    path('admin/', admin.site.urls), # This single line pulls in all admin code
]
```

---

## Quesion? explain more about the `users` we are creating with `uv run python manage.py createsuperuser`. are these users same as the noraml `users` table we create in say `node` to store users information?

The users you create for the Django Admin are stored in the exact same `users` table as regular web-app users. In Django, there is no separate database table for administrators and standard users.

Here is exactly how Django manages this behind the scenes:

### 1. One Unified Table

All users — whether they are a site administrator, a moderator, or a regular customer registering on your website—live in the exact same database table (by default, `auth_user`).

### 2. Roles are Determined by Flags (Columns)

Django separates roles using specific Boolean columns (flags) inside that single user table. When you ran `createsuperuser`, Django created a row in that table and set specific permissions to `True`.

Here is how Django identifies the roles:

- **Regular Web-App User:** `is_staff = False`, `is_superuser = False`. (They can log into your main website, but they are completely blocked from entering `/admin/`).
- **Staff/Moderator:** `is_staff = True`, `is_superuser = False`. (They can log into `/admin/` but can only see or edit specific data you permit).
- **Admin (Superuser):** `is_staff = True`, `is_superuser = True`. (They have absolute control over everything in `/admin/`).

### 3. Sharing the Table in Your App

When you build your actual web application features (like a user registration page or a customer login form), you will write code that queries this exact same table.

## Question? what if i want to have additional filelds for users?

You **do not need to create a user model from scratch** because Django gives you a fully functional, production-ready user model right out of the box.

However, you _will_ write your own views, forms, and HTML pages to handle the user registration and login screens for your public web-app.

Here is exactly how developers handle this in Django:

### 1. You Use Django's Built-in Model

Django provides `django.contrib.auth.models.User`. This built-in model already has fields for:

- `username`
- `password` (automatically hashed for security)
- `email`
- `first_name` and `last_name`

When you build your registration form, you point it to this built-in model.

### 2. The Standard Best Practice: "AbstractUser"

Even though Django provides a built-in model, the official Django documentation strongly recommends that you **subclass** it on day one. This gives you the power to add custom fields later (like a phone number or bio) without breaking your database.

You do this by creating a simple model in your app's `models.py`:

```python
from django.contrib.auth.models import AbstractUser
class CustomUser(AbstractUser):
    # Add your own custom fields here later if you want
    phone_number = models.CharField(max_length=15, blank=True)
```

Then, you tell Django to use your model instead of the default one by adding this to `settings.py`:

```python
AUTH_USER_MODEL = 'myapp.CustomUser'
```

### 3. You DO Create the Registration Logic

While Django provides the database table (the model) and ready-to-use login/logout views, it does **not** provide a default public registration HTML page. You will write:

- A **Form** to accept the signup details.
- A **View** to validate the data and save the user.
- An **HTML Template** to show the signup form to your visitors.

---
