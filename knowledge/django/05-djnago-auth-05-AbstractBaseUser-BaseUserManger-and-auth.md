# `User`, `AbstractUser`, `AbstractBaseUser` , `BaseUserManager` , `PermissionMixin` and django AUTH

## `User` , `AbstractUser`, `AbstractBaseUser`, `BaseUserManager` and `PermissionMixin`

**these five classes form the bedrock of the built-in authentication system.** They offer varying levels of control to handle user data, login logic, and access permissions.

Here is a quick summary of how they relate to one another before diving into the details:

| **Class**              | **What it provides**                                                       | **Best Use Case**                                                             |
| ---------------------- | -------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| **`User`**             | Fully configured, production-ready model with standard fields.             | Quick prototypes or very basic websites.                                      |
| **`AbstractUser`**     | A full set of default fields, but customizable.                            | Adding new fields (like `bio` or `birthdate`) while keeping `username` login. |
| **`AbstractBaseUser`** | Bare-bones core mechanics only (password hashing and sessions).            | Total rewrite, like using `email` instead of `username` to log in.            |
| **`BaseUserManager`**  | The database helper to create rows, hash passwords, and handle superusers. | Required whenever you implement `AbstractBaseUser`.                           |
| **`PermissionsMixin`** | Fields and tracking logic for Groups, Flags, and Permissions.              | Paired with `AbstractBaseUser` to retain standard Django admin rights.        |

---

### 1. User

The User class is Django's **default, ready-to-use user model**.

- **What it has:** Includes pre-defined fields like `username`, `first_name`, `last_name`, `email`, `password`, `is_staff`, `is_active`, and `is_superuser`.
- **Limitation:** It is highly rigid. If you use it and decide later that you want to drop usernames and log in using an email address, migrating the database becomes incredibly difficult.
- **Verdict:** Avoid using it for new production projects. Use a custom model instead.

### 2. AbstractUser

The `AbstractUser` class is an abstract model that **contains the exact same fields as the default `User` model**, but allows you to subclass it to add your own fields.

- **How it works:** It inherits from `AbstractBaseUser` and `PermissionsMixin` behind the scenes, providing the standard username-based authentication setup.
- **When to use:** Use this if you are perfectly happy logging users in via a `username`, but you want to attach extra profile fields directly to the user (e.g., `phone_number`, `profile_picture`, `address`).

### 3. AbstractBaseUser

The `AbstractBaseUser` class is a completely blank slate for an authentication model.

- **What it provides:** It provides only the absolute core mechanics required for authentication: secure password hashing (`password`), session tracking (`last_login`), and the backend login infrastructure.
- **What it lacks:** It does not include any fields like `email`, `username`, or name fields. You must explicitly write every database field you want. [6]
- **Configuration:** You must declare a `USERNAME_FIELD` (the unique database string used for logging in, such as `email`) and a list of `REQUIRED_FIELDS` for creating superusers through the command line.
- **When to use:** Use this when you want full control over your schema—most commonly when you want to replace `username` entirely with `email` as the unique login credential.

### 4. BaseUserManager

Models in Django use a "Manager" class to handle table-level queries (like `User.objects.create()`). `BaseUserManager` is the helper class that dictates how users are saved to the database.

- **Why it matters:** If you create a custom user model using `AbstractBaseUser`, Django no longer knows how to structure a normal user versus an administrative superuser.
- **Methods:** You must subclass `BaseUserManager` and override two essential methods:
  1.  **`create_user()`:** Validates inputs, normalizes email addresses to lowercase, safely hashes raw passwords, and saves the user instance.
  2.  **`create_superuser()`:** Calls `create_user()` but automatically flags the user as an administrator (`is_staff=True`, `is_superuser=True`).

### 5. PermissionsMixin

The `PermissionsMixin` is a modular tool that **injects Django’s built-in group and permission framework into your custom user model**.

- **The Problem:** If you use `AbstractBaseUser`, you lose the native ability to assign specific user permissions, group rules, and standard Django Admin dashboard controls.
- **The Solution:** By adding `PermissionsMixin` as a parent class next to `AbstractBaseUser`, your custom model automatically inherits:
  - Database fields like `is_superuser`, `groups`, and `user_permissions`.
  - Core permission checking methods like `has_perm()` and `has_module_perms()`.

---

## `AbstractBaseUser`, `BaseUserManager` and `PermissionMixin` in depth

To understand `AbstractBaseUser`, `BaseUserManager`, and `PermissionsMixin` deeply, you have to look at them as a **three-part ecosystem**. When you want total control over your user model (like using an email instead of a username to log in), Django requires you to use these three components together.

Here is the deep dive into how each component works, what happens under the hood, and how they connect.

---

### 1. `AbstractBaseUser` (The Authentication Core)

`AbstractBaseUser` provides the absolute bare minimum required for a model to function as a user model in Django. It does not care about fields like names, emails, or admin flags; it only cares about **securely identifying a session**.

#### What it includes under the hood:

- **`password` field:** A `CharField` that automatically handles encrypted storage.
- **`last_login` field:** A `DateTimeField` that keeps track of the user's last session.
- **Password Hashing Mechanics:** It includes the core methods to check and set passwords safely, such as `set_password()`, `check_password()`, and `set_unusable_password()`.

#### Critical attributes you must define:

When you inherit from `AbstractBaseUser`, you are forced to tell Django how your custom authentication should behave by defining these variables:

- **`USERNAME_FIELD`:** A string naming the field that acts as the unique identifier for logging in (e.g., `USERNAME_FIELD = 'email'`). This field must have `unique=True` in its model definition.
- **`REQUIRED_FIELDS`:** A list of field names that Django will prompt for when a developer runs the `python manage.py createsuperuser` command in the terminal. (Do not include the `USERNAME_FIELD` or `password` here).
- **`is_active` property/field:** Django's auth backend expects an `is_active` attribute to verify if a user is allowed to log in.

---

### 2. `BaseUserManager` (The Database Operations Coordinator)

Models in Django define the data structure, but **Managers** handle database interactions (saving, filtering, and creating rows). Because `AbstractBaseUser` can have any custom fields you want, Django's default database manager doesn't know how to create a user safely anymore. You must write a custom manager by subclassing `BaseUserManager`.

#### Why you cannot use a standard manager:

Passwords cannot be saved as plain text in the database. If you use standard `User.objects.create(password="my_password")`, it writes the plain string to the database, breaking the login system. `BaseUserManager` gives you the hooks to intercept and encrypt data before it hits the database.

### The two essential methods you must override:

1. **`create_user(*args, **kwargs)`:**
   - **Normalization:** It usually handles `self.normalize_email(email)`, which converts the domain part of an email address to lowercase so `User@Domain.com` and `user@domain.com` match.
   - **Encryption:** It takes the raw password string and encrypts it using `user.set_password(password)`.
   - **Saving:** It saves the instance using `user.save(using=self._db)`.
2. **`create_superuser(*args, **kwargs)`:**
   - It calls the `create_user` method above to ensure the admin's password is also encrypted.
   - It automatically forces crucial configuration flags to `True` (e.g., `is_staff=True`, `is_superuser=True`) so the user can immediately log into the Django Admin dashboard.

---

### 3. `PermissionsMixin` (The Authorization Extension)

`AbstractBaseUser` handles **authentication** (proving who you are), but it knows absolutely nothing about **authorization** (proving what you are allowed to do). If you only inherit from `AbstractBaseUser`, your custom user cannot use Django's built-in group system or the permissions checkmarks in the Admin panel.

`PermissionsMixin` is an abstract model that bridges this gap. By mixing it into your class inheritance, it injects Django's complex security architecture directly into your custom model.

#### What it injects into your User Model:

- **`is_superuser`:** A boolean flag. If `True`, Django completely bypasses specific checks and grants the user access to absolutely every view, model, and action in the system.
- **`groups`:** A Many-to-Many relationship to Django’s built-in `Group` model. This allows you to categorize users (e.g., "Editors", "Managers") and assign permissions to the group rather than individual users.
- **`user_permissions`:** A Many-to-Many relationship directly to Django's `Permission` model for granular, per-user overrides.
- **Utility Methods:** It provides helper methods that Django's system uses behind the scenes to verify access, most notably:
  - `has_perm(perm, obj=None)`: Returns `True` if the user has a specific permission string (like `'apps.add_product'`).
  - `has_module_perms(app_label)`: Returns `True` if the user is allowed to view the database tables for a specific app package.

---

### Synthesizing the Three: Complete Blueprint Architecture

Here is exactly how these three components assemble in a real-world scenario to replace the classic username login with an **email-based login system**:

```python

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# 1. Custom Manager handles database writing logic
class MyCustomUserManager(BaseUserManager):

    def create_user(self, email, first_name, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must provide an email address")

        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, **extra_fields)

        user.set_password(password) # Safely hashes the password string
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, password=None, **extra_fields):
        # Force permission flags required by PermissionsMixin
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        return self.create_user(email, first_name, password, **extra_fields)


# 2. Custom Model uses AbstractBaseUser for session core, and PermissionsMixin for access controls
class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50)
    date_joined = models.DateTimeField(auto_now_add=True)

    # Core flags required by Django's internal auth engine
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False) # Controls Admin site access

    # 3. Connect the custom database manager to the model
    objects = MyCustomUserManager()

    # Tells Django to look for 'email' instead of 'username' during login
    USERNAME_FIELD = 'email'

    # Prompted during 'createsuperuser' terminal wizard (alongside email and password)
    REQUIRED_FIELDS = ['first_name']

    def __str__(self):
        return self.email

```

### Summary of Interdependence

- **`AbstractBaseUser`** defines **who** can create a session (authenticates via passwords).
- **`BaseUserManager`** defines **how** to securely save that user data and format credentials.
- **`PermissionsMixin`** defines **what** that authenticated user is allowed to modify once they log in.

---

## Login process

Django divides the login process into separate components: a controller (**`LoginView`**), a coordination function (**`login()`**), a verification function (**`authenticate()`**), and an underlying engine called an **Authentication Backend**.

Here is how they fit together, what each component does, and the step-by-step lifecycle of a login request.

---

### The 4 Core Components Explained

#### 1. LoginView (The Traffic Controller)

`LoginView` is a built-in, ready-to-use Class-Based View. It handles the entire HTTP request/response cycle for logging in.

- **GET Request:** It displays the login webpage using an HTML template.
- **POST Request:** It captures the credentials (username/email and password) submitted by the user, runs form validation (checking for empty fields), and starts the backend verification process.

#### 2. authenticate() (The Verifier)

`authenticate()` is a standalone Django utility function. Its only job is to look at the raw credentials and answer the question: **"Are these credentials valid, and do they match a user in the database?"**

- It does not log the user in; it only inspects inputs.
- It accepts keyword arguments like `username` (or `email`) and `password`.
- If the credentials match a valid user, it returns that specific **`User` object**.
- If the credentials are wrong or the user is inactive, it returns **None**.

#### 3. Authentication Backend (The Security Engine)

`authenticate()` does not actually search the database itself; it delegates that work to one or more **Authentication Backends**.

- A backend is a plain Python class specified in your `settings.py` file under the `AUTHENTICATION_BACKENDS` list.
- By default, Django uses `ModelBackend`, which checks the credentials against your database using standard Django ORM queries.
- **How it operates:** It fetches the user record, runs `AbstractBaseUser.check_password()` to compare hashes, and flags which specific backend successfully verified the user.

#### 4. login() (The Session Creator)

`login()` is another standalone Django utility function. It takes an already authenticated user and officially signs them into the web session.

- It modifies the incoming HTTP request.
- It generates a unique **Session ID**, stores it in Django’s server-side session database, and attaches that Session ID as a cookie to the user's browser.
- It also marks the `last_login` timestamp on the user model.

---

### How They Work Together: The Execution Lifecycle

When a user visits your `/login/` URL, fills out the form, and hits **Submit**, the components work together in a strict sequential order:

```text

[User Browser]
      │  (POST Credentials)
      ▼
 1. LoginView (Receives request, validates form text)
      │
      ▼
 2. authenticate() (Forwards credentials to find a match)
      │
      ▼
 3. Auth Backend (Queries DB, checks AbstractBaseUser password hash)
      │
      ▼  (Returns User Object if valid)
 4. login() (Receives User Object, creates session cookie)
      │
      ▼
[User Browser] (Redirected to Home Page, now officially logged in)

```

### Step-by-Step Code Execution Under the Hood:

1. **`LoginView` takes the hit:** The user submits the form. `LoginView` captures the data and passes it to an internal form wrapper (`AuthenticationForm`).
2. **`LoginView` calls `authenticate()`:** Inside `LoginView`, Django executes a line of code that looks like this:

   ```python
   user = authenticate(username=cleaned_email, password=cleaned_password)
   ```

3. **`authenticate()` loops through the Backends:** The `authenticate()` function checks `settings.py` for your active engines. It hands the credentials to `ModelBackend`. The backend runs:

   ```python

   # 1. Finds the user in the database
   user = CustomUser.objects.get(email=cleaned_email)
   # 2. Uses AbstractBaseUser mechanics to check the password hash
   if user.check_password(cleaned_password):
       return user
   ```

   If successful, the backend attaches a hidden attribute to the user object (`user.backend = 'django.contrib.auth.backends.ModelBackend'`) so Django remembers _how_ this user got in.

4. **`LoginView` inspects the result:**
   1. If `user` is `None`, `LoginView` re-renders the page with an error ("Invalid username or password").
   2. If a valid `user` object is returned, `LoginView` moves forward.
5. **`LoginView` calls `login()`:** Now that the identity is proven, LoginView establishes the persistent session:

   ```python
   login(request, user)
   ```

   The `login()` function updates the `last_login` field, drops a secure `sessionid` cookie into the user's browser, and returns a success response.

6. **Redirection:** `LoginView` reads your `LOGIN_REDIRECT_URL` setting (e.g., `/dashboard/`) and routes the user's browser to their landing page.

---

### Why is it split up like this? (The Benefit of Modularity)

Django decouples these components so you can modify parts of the system without rewriting the whole pipeline.

- **Want to change the login page layout?** Overwrite the `LoginView` template layout. You don't have to touch database code.
- **Want to implement Single Sign-On (SSO), OAuth, or LDAP?** Leave `LoginView`, `authenticate()`, and `login()` completely alone. Just write a custom **Authentication Backend** class that checks an external API instead of your local database. Django will seamlessly handle the rest of the web cycle.
