# Django naming standards

Django/Python has established naming conventions, and it's better to follow them rather than use kebab-case globally.

## Recommended Django/Python naming

| **Thing**             | **Recommended**        | **Example**          |
| --------------------- | ---------------------- | -------------------- |
| Django app            | `snake_case`           | `user_management`    |
| Python files          | `snake_case`           | `user_service.py`    |
| Python variables      | `snake_case`           | `user_profile`       |
| Python functions      | `snake_case`           | `get_user_profile()` |
| Python classes        | `PascalCase`           | `UserProfile`        |
| Constants             | `UPPER_SNAKE_CASE`     | `MAX_LOGIN_ATTEMPTS` |
| Django model          | `PascalCase`           | `UserProfile`        |
| Django URL name       | `snake_case`           | `user_profile`       |
| URL path              | **kebab-case is fine** | `/user-profile/`     |
| HTML/CSS/JS filenames | usually `kebab-case`   | `user-profile.html`  |

For example, this is a good Django structure:

```text
my_project/
├── manage.py
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── users/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── serializers.py
│   └── services/
│       └── user_service.py
│
└── templates/
    └── users/
        └── user-profile.html
```

And in `urls.py`:

```python
urlpatterns = [
    path("user-profile/", views.user_profile, name="user_profile"),
]
```

Notice the distinction:

```text
URL path:     user-profile       ← kebab-case
Python name:  user_profile       ← snake_case
function:     user_profile()     ← snake_case
class:        UserProfile        ← PascalCase
```

### What about camelCase?

For a Django/Python project, I would **avoid camelCase for Python identifiers**:

```python
# ❌ Avoid
userProfile = ...
getUserProfile()

# ✅ Prefer
user_profile = ...
get_user_profile()
```

Python's official style guide, **PEP 8**, uses `snake_case` for functions and variables and `CapWords`/PascalCase for classes.

> **Use `snake_case` for Python/Django identifiers, `PascalCase` for classes, and `kebab-case` for URL paths and frontend-facing filenames where appropriate.**
