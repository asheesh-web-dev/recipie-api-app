# `related_name`, `related_query_name` attributes and their quirks

- [`related_name` and `related_query_name`](#related_name-and-related_query_name)
- [Filed Lookup using`__` , a bridge. It _**connects models, fields, and operations together**](#field-lookups-in-django)
- [Question? When we can access the the reverse relationship using `related_name`. then why the need for `related_query_name`. they sound doing same job. and the issue with `related_name` in AbstractModels having relationships.](#when-we-can-access-the-the-reverse-relationship-using-related_name-then-why-the-need-for-related_query_name-they-sound-doing-same-job-and-the-issue-with-related_name-in-abstractmodels-having-relationships)
- [Question? is it compulosry to define `realted_name` , `related_query_name` in realtionships](#question-is-it-compulosry-to-define-realted_name--related_query_name-in-realtionships)

---

---

## `related_name` and `related_query_name`

- tags and books having many to many relationship
- user and posts having one to many relationships
- user and user_profile having one to one realtionship

Here is how `related_name` and `related_query_name` work across all three relationship types, using your exact models.

### 1. One-to-One: User & UserProfile

In a `OneToOneField`, the reverse relationship returns a **single object** instead of a manager (queryset).

#### The Models

```python

from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    user = models.OneToOneField(
    User,
    on_delete=models.CASCADE,
    related_name="profile", # Used for object access
    related_query_name="profile_query" # Used for filtering
    )
    bio = models.TextField()

```

#### How to Use It

- **`related_name` (Object Access):**

```python

# Access the profile directly from the user instance
my_user = User.objects.get(username="alice")
print(my_user.profile.bio)

```

- **`related_query_name` (Filtering):**

```python
# Find users whose profile bio contains the word 'Django'
devs = User.objects.filter(profile_query__bio__icontains="Django")
```

---

### 2. One-to-Many: User & Post

In a `ForeignKey` relationship, the reverse lookup returns a **manager** containing multiple objects.

#### The Models

```python

class Post(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts", # Customizes user.post_set.all() -> user.posts.all()
        related_query_name="post_query" # Customizes lookups
    )
    title = models.CharField(max_length=200)

```

#### How to Use It

- **`related_name` (Object Access):**

```python

# Fetch all posts written by this specific user
my_user = User.objects.get(username="bob")
user_posts = my_user.posts.all()

```

- **`related_query_name` (Filtering):**

```python

# Find all users who wrote a post with 'Tutorial' in the title
authors = User.objects.filter(post_query__title__icontains="Tutorial")

```

---

### 3. Many-to-Many: Book & Tag

In a `ManyToManyField`, both sides return a **manager** because books can have many tags, and tags can belong to many books.

#### The Models

```python

class Tag(models.Model):
    name = models.CharField(max_length=50)

class Book(models.Model):
    title = models.CharField(max_length=200)
    tags = models.ManyToManyField(
        Tag,
        related_name="books", # Customizes tag.book_set.all() -> tag.books.all()
        related_query_name="book_query" # Customizes lookups
    )

```

#### How to Use It

- **`related_name` (Object Access):**

```python

# Get all books associated with a specific tag
my_tag = Tag.objects.get(name="Python")
python_books = my_tag.books.all()

```

- **`related_query_name` (Filtering):**

```python

# Find all tags attached to books that have 'Cookbook' in the title
cooking_tags = Tag.objects.filter(book_query__title__icontains="Cookbook")

```

---

### Summary Cheat Sheet

| **Relationship Type** | **`related_name` returns**               | **`related_query_name` changes**                        |
| --------------------- | ---------------------------------------- | ------------------------------------------------------- |
| **OneToOneField**     | A single model instance (`user.profile`) | Filter keys (`User.objects.filter(profile_query__...)`) |
| **ForeignKey**        | A related manager (`user.posts.all()`)   | Filter keys (`User.objects.filter(post_query__...)`)    |
| **ManyToManyField**   | A related manager (`tag.books.all()`)    | Filter keys (`Tag.objects.filter(book_query__...)`)     |

---

---

## Field Lookups in Django

```python

User.objects.filter(profile_query__bio__icontains="Django")

```

explain the use of `__`

---

In Django, the double underscore (`__`) acts as a bridge. It _**connects models, fields, and operations together** inside your filter queries_.

Because standard Python dots (`.`) cannot be used inside keyword arguments (like `filter(user.bio="...")`), Django uses `__` to parse your query and translate it into SQL.

**[Read More about Field Lookups in Django](./08-django-orm-02-relationships-02-the-field-lookup-dunder-as-bridge.md#field-lookup--dunder-__-as-bridget-between-models-fields-and-operations)**

---

---

## When we can access the the reverse relationship using `related_name`. then why the need for `related_query_name`. they sound doing same job. and the issue with `related_name` in AbstractModels having relationships.

No, they are **not the same**. While they sound similar, they serve two entirely different purposes in Django.
Here is the short answer:

- **`related_name`** is used for Python object attribute lookup (e.g., `user.profile`).
- **`related_query_name`** is used for **Django QuerySet filtering** inside `.filter()` and `.exclude()` methods (e.g., `User.objects.filter(my_query_name__bio="Hello")`).

By default, you rarely need to touch `related_query_name` because Django automatically defaults it to whatever you set for your `related_name`.

> > **[Is it compulsory to define `related_name` and `realted_query_name` ?](#question-is-it-compulosry-to-define-realted_name--related_query_name-in-realtionships)**

### The Practical Difference (Code Example)

Let's look at a schema where we override **both** properties to see exactly how they split duties.

```python


from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(
    User,
    on_delete=models.CASCADE,
    related_name='profile_attribute', # <--- For python object access
    related_query_name='profile_filter' # <--- For QuerySet filtering
    )
    bio = models.TextField()

```

#### 1. How `related_name` behaves:

This targets an **instantiated Python object** in your code.

```python

user_obj = User.objects.get(id=1)

# Works! Uses related_name
print(user_obj.profile_attribute.bio)

# FAILS with AttributeError! You cannot use related_query_name here
print(user_obj.profile_filter.bio)

```

#### 2. How `related_query_name` behaves:

This targets database lookups when you are writing **SQL-generating queries**.

```python

# Works! Uses related_query_name
# fetch all users who are developers.
active_users = User.objects.filter(profile_filter__bio__icontains="Developer")

# FAILS with FieldError! You cannot use related_name inside filter() here
active_users = User.objects.filter(profile_attribute__bio__icontains="Developer")

```

---

### What is the "problem" with related_name that forces us to use related_query_name?

There is no "problem" with `related_name` — it works perfectly. You only need to explicitly declare `related_query_name` when you want your **Python syntax** to read differently than your **database query syntax**.

The most common reason developers override `related_query_name` is **Model Inheritance** (Abstract Base Models).

#### The Abstract Model Problem

When multiple Django models inherit from an **Abstract Base Model**, they copy all of its fields exactly as they are written.

If you put a plain text string like `related_name='reviews'` inside an abstract model, you create a clash that breaks Django's reverse lookup system.

Here is exactly why that happens and how the placeholder fixes it.

##### The Problem: The Naming Collision

Imagine you have this setup without placeholders:

```python

class BaseReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')

    class Meta:
        abstract = True  # This model won't create a database table itself


# Django duplicates the fields into these real tables:
class BookReview(BaseReview):
    pass

class MovieReview(BaseReview):
    pass

```

Because of inheritance, Django attempts to create two reverse shortcuts on your `User` model:

1. `user.reviews` -> points to **BookReview** records.
2. `user.reviews` -> points to **MovieReview** records.

This creates a collision. If you type `user.reviews.all()`, Django has no way of knowing whether you want book reviews or movie reviews. To prevent this ambiguity, Django halts execution and throws a **SystemCheckError (fields.E304 / fields.E305)** stating that the reverse accessor clashes.

##### The Solution: The `%(class)s` Placeholder

To fix this, Django allows you to use a special placeholder text string: `%(class)s` (written in lowercase).

During app initialization, Django scans your models, finds the classes inheriting from the abstract base, and dynamically swaps out `%(class)s` with the **lowercase name of the child model.**

```python

class BaseReview(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='%(class)s_reviews' # <--- Dynamic placeholder
    )

    class Meta:
        abstract = True

```

##### What Django automatically generates behind the scenes:

For the `BookReview` child class, it compiles to:

- **`related_name='bookreview_reviews'`**
- Python access: `user.bookreview_reviews.all()`

For the `MovieReview` child class, it compiles to:

- **`related_name='moviereview_reviews'`**
- Python access: `user.moviereview_reviews.all()`

By adding that tiny placeholder, every child model gets a uniquely isolated reverse relationship attribute name, completely resolving the conflict.

#### Other Placeholders You Can Use

Django supports two formatting placeholders in abstract model fields:

- **`%(class)s`:** Replaced by the lowercase name of the child class.
- **`%(app_label)s`:** Replaced by the lowercase name of the app the child class is defined in (crucial if your child models live in different Django apps).

### Summary Cheat Sheet

- Use **`related_name`** when you want to change how you talk to a reverse relationship in **pure Python** (using dots: `object.attribute`).
- Use **`related_query_name`** when you want to change the **keyword argument string** used inside database filtering methods (using double underscores: `filter(keyword__field)`).

---

---

## Question? is it compulosry to define `realted_name` , `related_query_name` in realtionships

**No, it is absolutely not compulsory.** In fact, you rarely need to define `related_query_name` manually in your day-to-day Django development.

Django is designed to be developer-friendly. If you omit `related_query_name`, Django uses an automatic fallback strategy so that your database filtering still works flawlessly.

---

### How Django Handles the Fallback

When you leave out `related_query_name`, Django uses the following fallback chain to determine what keyword you should use inside your `.filter()` methods:

1. **If you defined a `related_name`:** Django uses that exact string as the `related_query_name`.
2. **If you did NOT define a `related_name`:** Django falls back to the **lowercase name of the model** containing the field.

---

### The Fallback in Action (Examples)

#### Scenario A: You only define `related_name` (Most Common)

```python

class Article(models.Model):
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stories')

```

- **Python Access:** `user.stories.all()`
- **Query Filter:** `User.objects.filter(stories__title__contains="Django")` _(Django automatically copied your related_name to use as the query name)_

#### Scenario B: You define nothing (Default Behavior)

```python

class Article(models.Model):
    reporter = models.ForeignKey(User, on_delete=models.CASCADE)

```

- **Python Access:** `user.article_set.all()` _(Django's default `_set` suffix)_
- **Query Filter:** `User.objects.filter(article__title__contains="Django")` _(Django automatically used the lowercase model name `article`)_

---

### When is it actually useful to define it?

You should only explicitly write out `related_query_name` in two specific edge cases:

1. **Plural vs. Singular preference:** You want your Python object syntax to read as a plural noun, but your database query syntax to read as a singular noun.

   ```python

   # related_name='articles'
   user.articles.all()

   # related_query_name='article' ->
   User.objects.filter(article__title="...")

   ```

2. **Abstract Model overrides:** [As discussed previously](), when using abstract base classes where you want a unified keyword for lookup across multiple child tables.

---

---
