# The `swappable` internal `Meta` class in auth `User` model

```python
# django/contrib/auth/models.py
class User(AbstractUser):
    """
    Users within the Django authentication system are represented by this
    model.

    Username and password are required. Other fields are optional.
    """

    class Meta(AbstractUser.Meta):
        swappable = "AUTH_USER_MODEL"
```

The `swappable` attribute is a **private, intentionally undocumented Django Meta option used to signal that a model can be completely swapped out or replaced by a custom user-defined model**.

It accepts a string pointing to a settings variable, such as `swappable = 'AUTH_USER_MODEL'`.

## Why Does Django Need It?

Django's migration and ORM frameworks are highly rigid. Normally, if a model (like `auth.User`) has foreign key relationships pointing to it from other apps, trying to completely delete that model and swap it for a custom class breaks the database schemas and relationships.

The `swappable` attribute tells Django: _"Do not treat this model as permanent. Look at the specified `settings.py` variable instead, and build database foreign keys pointing to whatever model the user specified there."_

## Where is it Used?

- **Built-in `User` Model:** The most famous example is inside Django's source code for the default `User` model.
- **Reusable Third-Party Packages:** Package maintainers use it so their libraries can dynamically adapt to whatever custom models an end-user has configured (e.g., custom OAuth tokens or profiles).

## Should You Use It in Your Own Code?

**No, you should almost never manually write swappable in your custom app models.**

1. **It is Private API:** Because it is an internal Django mechanism, it can change without warning in future versions of Django.
2. **If You are Making a Custom User:** When you subclass `AbstractUser` to make your own custom user model, you **do not** add `swappable` to your new class. Only the _base model_ being replaced needs to declare it. You simply point your `settings.py` to your new model using `AUTH_USER_MODEL = 'myapp.CustomUser'`.
3. **If You Truly Need Custom Swappable Models:** If you are a library author building a package that requires other users to swap out your models, do not write it from scratch. Use an ecosystem-accepted library like [django-swappable-models (Swapper)](https://github.com/openwisp/django-swappable-models) which abstracts Django's fragile internal migration logic.
