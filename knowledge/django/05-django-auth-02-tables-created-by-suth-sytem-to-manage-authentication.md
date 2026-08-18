# tables created by django to mangage authentication

When you run `python manage.py migrate` on a fresh Django installation, Django creates a **standard** set of database tables. These tables are generated primarily by two core entries in your `INSTALLED_APPS`: `django.contrib.auth` and `django.contrib.contenttypes`.

Together, they establish the **infrastructure** needed to log users in, map system actions to account permissions, track user groups, and manage browser states.

---

## Core Authentication & Authorization Tables (`django.contrib.auth`)

### 1. auth_user

This is the main user registry table. If you use Django's default User or AbstractUser configuration, this table houses core user profile information.

- Key Columns: id, password, username, email, first_name, last_name, is_staff, is_active, is_superuser, last_login, date_joined.
- Note: If you create a custom user model in an app named accounts, this table name will dynamically switch to your app prefix (e.g., accounts_customuser).

### 2. auth_group

Stores the names of user categories or system roles (e.g., "Moderator", "Premium Customer").

- Key Columns: id, name.

### 3. auth_permission

Contains an exhaustive roster of actions available across your models. Django automatically pre-populates this table with four foundational choices for every model you register (add, change, delete, view).

- Key Columns: id, name, content_type_id, codename (e.g., add_blogpost).

---

## Many-to-Many Bridge Tables

Because a single user can have multiple individual permissions or join various structural groups, Django maintains relational link tables to cleanly stitch the profiles together:

### 4. auth_user_groups

Maps users directly to groups. A user can belong to multiple groups, and a group can contain multiple users.

- Key Columns: id, user_id, group_id.

### 5. auth_user_user_permissions

Maps specific permissions straight to individual users, completely bypassing group logic. Use this when a single user requires unique overrides.

- Key Columns: id, user_id, permission_id.

### 6. auth_group_permissions

Defines the permissions assigned to an entire group. Any user assigned to a group inherits all the permissions logged in this bridge.

- Key Columns: id, group_id, permission_id.

---

## Supporting Core Infrastructure Tables

While not directly built inside the auth module, the authorization architecture cannot run without these two companion tables:

### 7. django_content_type

Managed by django.contrib.contenttypes, this table acts as a global index for every model in your system. Every row tracks an exact model name tied to its native Django application module. The auth_permission table relies directly on these foreign keys to connect generic permission rules to specific tables.

- Key Columns: id, app_label, model.

### 8. django_session

Managed by django.contrib.sessions, this table makes stateless web browsers recognize user persistence. When a client completes authentication, Django stores encrypted data (including the verified user's database ID) inside this table, issuing a matching sessionid token via browser cookies.

- Key Columns: session_key, session_data, expire_date.

---

## Visual Database Entity Relationship (ER) Map

```text
        [ auth_user ] <════ (M2M) [auth_user_groups] ════> [ auth_group ]
             ║                                                    ║
           (M2M)                                                (M2M)
             ║                                                    ║
             ▼                                                    ▼
    
[ auth_user_user_permissions ]                         [ auth_group_permissions ]
             ║                                                    ║
             ╚══════════════> [ auth_permission ] <═══════════════╝
                                     ║
                                (Foreign Key)
                                     ▼
                           [ django_content_type ]
```
---
