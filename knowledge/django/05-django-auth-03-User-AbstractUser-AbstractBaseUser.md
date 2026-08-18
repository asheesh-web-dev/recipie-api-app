# Table of Contents

- [`User`, `AbstractUser` and `AbstractBaseUser`](#user-abstractuser-and-abstractbaseuser)
    - [``User` (The Default Model)](#1-user-the-default-model)
    - [`AbstractUser` (The Recommended Choice)](#2-abstractuser-the-recommended-choice)
    - [`AbstractBaseUser` (The Total Control Choice)](#3-abstractbaseuser-the-total-control-choice)
    - [Summary Comparison Table](#summary-comparison-table)
- [`CustomManager` and its need](#custommanager-and-its-need)
    - [Why Do You Need a Custom Manager?](#why-do-you-need-a-custom-manager)
    - [Code Example: A Custom Manager for Email Login](#code-example-a-custom-manager-for-email-login)
    - [Linking the Manager to Your Model](#linking-the-manager-to-your-model)
- [`models.Manager` and creation of `BaseUserManager`](#modelsmanager-and-creation-of-baseusermanager)
    - [Part 1: What is `models.Manager` and Why Do We Need It?](#part-1-what-is-modelsmanager-and-why-do-we-need-it)
        - [Why We Need It](#why-we-need-it)
        - [Example of Modifying `models.Manager`](#example-of-modifying-modelsmanager)
    - [Part 2: The Core Logic and Necessity of `BaseUserManager`](#part-2-the-core-logic-and-necessity-of-baseusermanager)
        - [The Underlying Logic](#the-underlying-logic)
        - [Why We Need to Write Our Own Implementation](#why-we-need-to-write-our-own-implementation)
- [`QuerySet` and its link to `psycopg` driver which executes raw sql queries](#queryset-and-its-link-to-psycopg-driver-which-executes-raw-sql-queries)
    - [What is a QuerySet?](#what-is-a-queryset)
    - [The Complete Execution Chain](#the-complete-execution-chain)
    - [Why Did Django Separate Manager and QuerySet?](#why-did-django-separate-manager-and-queryset)
    - [Question? is `QuerySet` built only for `SELECT` queries](#queryset-and-its-link-to-psycopg-driver-which-executes-raw-sql-queries)
        - [How QuerySets Handle Different SQL Commands](#how-querysets-handle-different-sql-commands)
            - [`SELECT` (Read)](#1-select-read)
            - [`UPDATE` (Update)](#2-update-update)
            - [`DELETE` (Destroy)](#3-delete-destroy)
            - [Why is `INSERT` Excluded?](#why-is-insert-excluded)

---

## `User`, `AbstractUser` and `AbstractBaseUser`

these three classes represent different tiers of control over your user data. The primary difference is **how much of Django's default behavior you want to keep versus rewrite.**

```text
[AbstractBaseUser]       <-- Bare minimum (Password hashing only)
        ▲
        │ (inherits from)
        │
[AbstractUser]           <-- Full default fields (Username, Email, First Name, etc.)
        ▲
        │ (inherits from)
        │
     [User]              <-- Built-in model (Ready out-of-the-box, hard to change later)

```

---

### 1. `User` (The Default Model)

This is the built-in concrete model that Django provides out of the box.

- **What it is:** A ready-to-use database table.
- **Fields included:** `username`, `password`, `email`, `first_name`, `last_name`, `is_staff`, `is_active`, `is_superuser`, `date_joined`, and `last_login`.
- **When to use it:** Only for small hobby projects, tutorials, or internal prototypes where a standard `username` and `password` setup is completely sufficient.
- **The Catch:** It is incredibly difficult to modify later if your project grows and you need to add custom fields like a profile picture or phone number.

### 2. `AbstractUser` (The Recommended Choice)

This is an abstract class that contains the exact same fields and behaviors as the default `User` model, but it is intentionally left open for you to subclass.

- **What it is:** A complete template of Django's default user setup that allows extensions.
- **Fields included:** All default fields (`username`, `email`, etc.).
- **When to use it:** **This is the best practice for 95% of new projects.** You use it when you are happy with how Django logs users in (using a username), but you want the freedom to add your own fields.
- **Example Usage:**

  ```python
  from django.contrib.auth.models import AbstractUser
  from django.db import models

  class CustomUser(AbstractUser):
      bio = models.TextField(blank=True)
      birth_date = models.DateField(null=True, blank=True)
  ```

### 3. `AbstractBaseUser` (The Total Control Choice)

This is the lowest-level abstract class available for authentication. It strips away almost everything except the foundational security mechanics.

- **What it is:** A bare-bones core that provides only password hashing, password resetting tracking, and basic token features. It does not include fields like `username`, `first_name`, or even default permissions features.
- **Fields included:** Only `password`, `last_login`, and `is_active` (which you must manage yourself).
- **When to use it:** Use this only when you want to fundamentally change how authentication works. The most common use case is swapping out the `username` field entirely to use an `email address` as the primary login ID.
- **The Catch:** You must write your own custom User Manager from scratch to handle account creation (create_user and create_superuser).

### Summary Comparison Table

| **Feature / Capability**     | \*_User_                | **AbstractUser**        | **AbstractBaseUser**          |
| ---------------------------- | ----------------------- | ----------------------- | ----------------------------- |
| **Database Table Created?**  | Yes, automatically      | No (Abstract)           | No (Abstract)                 |
| **Includes Default Fields?** | Yes                     | Yes                     | No (Only password mechanics)  |
| **Can add custom fields?**   | No (Not easily)         | Yes (Easiest way)       | Yes                           |
| **Can change Login Field?**  | No (Locked to username) | No (Locked to username) | Yes (e.g., Use Email instead) |
| **Requires Custom Manager?** | No                      | No                      | Yes (Mandatory)               |

## `CustomManager` and its need

A **Custom Manager** in Django is a class used to modify how database queries are constructed for a specific model, or to add dedicated helper methods for creating and manipulating data.

Every Django model has at least one manager, which is accessed using the `objects` attribute (e.g., `User.objects.all()`). When you build a highly customized user model, Django's default manager doesn't know how to handle your changes, requiring you to write a custom one.

### Why Do You Need a Custom Manager?

There are two primary reasons to create a custom manager:

1.  **To modify database creation logic (Mandatory for `AbstractBaseUser`)**
2.  **To add reusable, custom query methods for clean code**

#### Reason 1: Handling Account Creation (The `AbstractBaseUser` Requirement)

When you use `AbstractBaseUser` to switch your login identifier from a `username` to an `email`, Django's built-in creation tools (`python manage.py createsuperuser` or the admin panel registration) will break.

The command-line tools rely on two specific methods to create users securely: `create_user()` and `create_superuser()`. A custom manager rewrites these methods to accept and validate your new custom fields (like `email`) instead of looking for a `username`.

#### Reason 2: Encapsulating Common Queries (Dry Code)

Instead of scattering complex database filters across all your views, you can hide that logic inside a custom manager method.

- **Without a Custom Manager (Messy Views):**

  ```python
  # You have to repeat this exact filter in every view that looks for active premium users
  premium_users = User.objects.filter(is_active=True, subscription_tier='premium')
  ```

- **With a Custom Manager (Clean Views):**

  ```python
  # Clean, readable, and reusable anywhere in your project
  premium_users = User.objects.premium()
  ```

### Code Example: A Custom Manager for Email Login

If you use `AbstractBaseUser` to log users in via `email`, you must inherit from `BaseUserManager` and override the creation methods. Here is exactly what that look like:

```python
from django.contrib.auth.models import BaseUserManager
from django.db import models

class CustomUserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
    """Creates and saves a standard User with the given email and password."""
        if not email:
            raise ValueError('The Email field must be set')

        # Normalize the email (lowercase the domain part)
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)

        # Automatically hashes the password securely before saving
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Creates and saves a Superuser with the given email and password."""
        # Ensure administrative permissions are set to True
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)
```

### Linking the Manager to Your Model

Once you write the manager, you attach it to your model using the `objects `attribute:

```python
from django.contrib.auth.models import AbstractBaseUser

class CustomUser(AbstractBaseUser):
    email = models.EmailField(unique=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    # Link the custom manager here
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'  # Tell Django to use email as the login ID
    REQUIRED_FIELDS = []       # Prompts for createsuperuser command
```

## `models.Manager` and creation of `BaseUserManager`

### Part 1: What is `models.Manager` and Why Do We Need It?

A **`models.Manager`** is the Python interface that sits between your Django code and your database. It is the tool that allows you to talk to your database tables using Python code instead of raw SQL queries.

Every Django model gets a default manager named **`objects`** automatically unless you change it. When you write `Product.objects.all()`, the `objects` part is the manager.

#### Why We Need It

```text
[ Your Django Code ] ──> [ models.Manager (objects) ] ──> [ Raw SQL Query ] ──> [ Database ]
```

1. **It is the Gateway to Querying:** Models represent a single row in a database table (e.g., a single user or single product). The Manager represents the entire table collection. You cannot filter, look up, or count records without it.
2. **It Keeps Views Clean (DRY - Don't Repeat Yourself):** Instead of cluttering your views with repetitive filters, you can write custom filters inside a manager.
3. **Database Abstraction:** It translates Python methods like `.filter()` or `.exclude()` into the correct SQL syntax for PostgreSQL, MySQL, or SQLite behind the scenes.

#### Example of Modifying `models.Manager`

If you have a blog, you might only want to display "published" posts. Instead of filtering manually everywhere, you create a custom manager:

```python
from django.db import models

# 1. Define the custom manager
class PublishedManager(models.Manager):

    def get_queryset(self):
        # Automatically filters out drafts
        return super().get_queryset().filter(status='published')

class Post(models.Model):
    title = models.CharField(max_length=200)
    status = models.CharField(max_length=10, default='draft')

    # 2. Attach it to the model
    objects = models.Manager() # Keep default manager
    published = PublishedManager() # Add custom manager

```

Now, in your views, you can simply call `Post.published.all()` to instantly get only published posts.

### Part 2: The Core Logic and Necessity of `BaseUserManager`

`BaseUserManager` is a specialized subclass of `models.Manager`. It was created by Django developers for one specific reason: **User accounts require security, strict validation, and administrative setup that regular database tables do not need.**

#### The Underlying Logic

Regular database records (like a blog post or a product) are straightforward text and numbers saved to a table. User accounts are highly sensitive and require complex business logic before they touch the database.

`BaseUserManager` contains the internal infrastructure to handle this logic safely through two primary architectural patterns:

##### 1. Cryptographic Password Hashing

You must never save plain-text passwords in a database. If someone signs up with the password `Secret123`, it must be converted into an unreadable string (a hash) like `pbkdf2_sha256$260000$....`

`BaseUserManager` provides the architectural hook (`user.set_password()`) that ensures passwords are intercepted, securely scrambled using modern cryptographic standards, and safely stored. A standard `models.Manager` knows nothing about encryption.

##### 2. Standardizing the Admin API Contract

Django features automated built-in tools like the `python manage.py createsuperuser` command line terminal and the visual Django Admin Panel. These automated tools need a predictable way to generate users.

They expect your manager to strictly expose two methods:

- `create_user()`
- `create_superuser()`

`BaseUserManager` serves as the blueprint providing the foundational structure for these methods so that Django's global administrative tools can communicate flawlessly with your custom database configuration.

### Why We Need to Write Our Own Implementation

When you use `AbstractBaseUser` to switch your authentication system (for example, logging in with an `Email` instead of a `Username`), Django’s default background logic shatters.

The framework no longer knows what fields are mandatory, what constitutes a valid login identifier, or how to flag an administrative account. You must create a class that inherits from `BaseUserManager` to explicitly map out these structural definitions.

If you omit this custom implementation, running `createsuperuser` will crash your console because Django will try to pass a username parameter into a database table that only accepts an `email`.

## `QuerySet` and its link to `psycopg` driver which executes raw sql queries

### What is a QuerySet?

A **`QuerySet`** is a collection of database queries wrapped in a Python list-like object. It represents a specific SQL select statement that has been built, **but not yet executed.**

When you write `Product.objects.filter(price__gt=10)`, the Manager (`objects`) immediately returns a `QuerySet` object.

The most important characteristic of a `QuerySet` is that it is **lazy**. Creating a QuerySet does not touch your database at all. It simply writes the blueprint of the SQL query in server memory.

### The Complete Execution Chain

Here is the exact order of operations showing where the `Manager`, `QuerySet`, and `psycopg` (the database driver) interact:

```text
[ Your Code ] ──> [ Manager ] ──> [ QuerySet ] ──> [ Django ORM Engine ] ──> [ DB Driver (psycopg) ] ──> [ Database ]
```

1. **The Manager (`models.Manager`):** This is just an entry point. When you call `.filter()` or `.all()`, the Manager internally calls `self.get_queryset().filter()`. It passes the job to a QuerySet.
2. **The QuerySet:** This builds and chain-links your query filters. If you write `.filter(status='active').exclude(stock=0)`, the QuerySet updates its internal SQL blueprint without running anything.
3. **The Trigger (Evaluation):** The database is hit only when you try to actually look at the data (e.g., looping over it with a `for` loop, printing it, converting it to a list, or checking its length).
4. **The Translation:** Once triggered, Django’s compiler turns the `QuerySet` blueprint into raw SQL string text.
5. **The Execution (`psycopg`):** Django hands that raw SQL string to your database driver (like `psycopg3` for PostgreSQL). The driver transmits the SQL to the actual database, grabs the rows, and hands them back to Django to be turned into Python objects.

### Why Did Django Separate Manager and QuerySet?

By separating the entry point (Manager) from the query builder (QuerySet), Django allows you to **chain queries together** easily.

Because a QuerySet method returns _another_ QuerySet, you can stack filters infinitely before hitting the database:

```python
# No database hits yet! It is just building the SQL statement.
query = Product.objects.filter(category='Electronics') # Manager returns QuerySet
query = query.filter(in_stock=True) # QuerySet returns QuerySet
query = query.order_by('-price') # QuerySet returns QuerySet

# The database is hit EXACTLY ONCE right here:
for product in query:
    print(product.name)

```

### Question? is `QuerySet` built only for `SELECT` queries

**No, a QuerySet is not built only for `SELECT` queries.** While it is most famous for retrieving data using `SELECT`, a QuerySet can also execute `UPDATE` and `DELETE` commands directly on the database.

However, it is never used for `INSERT` queries.

#### How QuerySets Handle Different SQL Commands

A `QuerySet` handles three out of the four major CRUD operations:

##### 1. `SELECT` (Read)    

This is the default behavior. Stacking filters prepares a `SELECT` statement.

```python
# Generates: SELECT \* FROM products WHERE price > 10;
products = Product.objects.filter(price\_\_gt=10)
```

##### 2. `UPDATE` (Update)

You can modify multiple database rows simultaneously by chaining the `.update()` method to a QuerySet. This executes a direct SQL `UPDATE` statement immediately without loading the objects into Python memory.

```python
# Generates: UPDATE products SET discount = 20 WHERE category = 'shoes';
Product.objects.filter(category='shoes').update(discount=20)

```

##### 3. `DELETE` (Destroy)

Similarly, you can remove rows instantly by chaining `.delete()`. This issues a direct SQL `DELETE` query to the database driver.

```python
# Generates: DELETE FROM products WHERE stock = 0;
Product.objects.filter(stock=0).delete()
```

#### Why is `INSERT` Excluded?

A QuerySet cannot perform an `INSERT` operation.

An `INSERT` creates a brand-new row in a table. Because a `QuerySet` represents a filtered set or collection of existing table rows, it makes no logical sense to filter a table to create something new.

To run an `INSERT` query, Django bypasses the QuerySet entirely and uses two other mechanisms:

- **The Model Instance:** Calling `.save()` on a single instance (e.g., `prod = Product(name="Shoes")` then `prod.save()`).
- **The Manager:** Calling the `.create()` method on the manager (e.g., `Product.objects.create(name="Shoes")`), which handles the insertion pipeline under the hood.
