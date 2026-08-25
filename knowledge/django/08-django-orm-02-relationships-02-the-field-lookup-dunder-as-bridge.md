# Field Lookup : dunder `__` as bridget between models, fields and operations

In Django, the double underscore (`__`) acts as a bridge. It connects models, fields, and operations together inside your filter queries.

Because standard Python dots (`.`) cannot be used inside keyword arguments (like `filter(user.bio="...")`), Django uses `__` to parse your query and translate it into SQL.

>> _Keyword arguments must follow the exact same naming rules as regular Python variables (identifiers). Allowed Characters - **Letters: `a-z` and `A-Z`** , **Numbers: `0-9`** (but cannot start the name), **Underscores: `_`**_


Here is a step-by-step guide from the absolute basics to advanced usage.

---

## Level 1: Basic Field Lookups (No Relationships)

At the most basic level, `__` attaches a **lookup operator** to a single field on the model you are querying.

**Syntax:** `field__operator=value`

```python

# 1. Exact match (case-insensitive)
# SQL: WHERE name LIKE 'alice'
Post.objects.filter(title__iexact="django tutorial")

# 2. Greater than (gt) and Less than (lt)
# SQL: WHERE views > 100
Post.objects.filter(views__gt=100)

# 3. Check if a value exists in a list
# SQL: WHERE status IN ('draft', 'published')
Post.objects.filter(status__in=['draft', 'published'])

# 4. Check for NULL values
# SQL: WHERE published_date IS NULL
Post.objects.filter(published_date__isnull=True)

```

---

## Level 2: Spanning One Relationship (Joining 2 Tables)

When you want to filter a model based on attributes of a connected model, `__` acts as a database `JOIN`.

**Syntax:** `relationship_name__target_field=value`

## Example: Find Posts based on Author info

```python

# Find all posts written by an author named 'Alice'
# Django looks at the 'author' ForeignKey, moves to the User model, and checks 'username'
posts = Post.objects.filter(author__username="alice")

```

## Example: The Reverse Direction (Using `related_query_name`)

If you start from the parent model (`User`) and want to look at the child model (`Post`), you use the `related_query_name` you defined earlier.

```python

# Find all users who have written a post with over 1000 views
users = User.objects.filter(post_query__views__gt=1000)

```
---

## Level 3: Deep Chaining (Joining 3+ Tables)

You can chain multiple double underscores together to travel across as many tables as your database relationships allow.

### The Scenario:

- A `Book` has a `ManyToManyField` to Tag.
- A `Book` has a `ForeignKey` to a publisher `User`.

### Example: Find Users based on Tag names

Let's find all Publishers (Users) who have published at least one book tagged with "Python".

```python


# Path: User -> Post/Book relation -> Tag relation -> Tag name field
tech_publishers = User.objects.filter(book_query__tags__name__iexact="Python")

```
- **`book_query`:** Jumps from `User` to `Book` table.
- **`tags`:** Jumps from `Book` to `Tag` table.
- **`name`:** Selects the **text column** on the `Tag` table.
- **`iexact`:** Applies the case-insensitive matching rule.

---

## Level 4: Special Lookups (Dates and Times)

Django provides specialized date extractors that utilize the `__` syntax to drill down into specific components of a datetime field.

```python

# Find all posts published in the year 2026
Post.objects.filter(published_date__year=2026)

# Find all posts published in the month of June (any year)
Post.objects.filter(published_date__month=6)

# Find all posts published on a Monday (Django uses 1 for Sunday, 2 for Monday... 7 for Saturday)
Post.objects.filter(published_date__week_day=2)

```
---

## Quick Reference Cheat Sheet

| **Syntax Example**                             | **What it tells Django to do**                                             |
| ------------------------------------------ | ---------------------------------------------------------------------- |
| `views__gte=10`                            | "Look at the `views` field; check if it is Greater Than or Equal to 10." |
| `title__startswith="A"`                    | "Look at the `title` field; check if it begins with 'A'."                |
| `author__profile_query__bio__isnull=False` | "Go to author, jump to their profile, check if the bio is not empty."  |

