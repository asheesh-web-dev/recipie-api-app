# REFERENTIAL INTEGRITY AND REFERETIAL ACTIONS WITH FOREIGN KEYS

When you attempt to delete a row from a parent table in PostgreSQL that is referenced by a foreign key in a child table, the outcome depends entirely on the **referential action** defined on that foreign key.

By default, PostgreSQL will **block the deletion and throw an error** if child records exist.

---

## The 5 Foreign Key Delete Behaviors

You can control this behavior using the `ON DELETE` clause when defining your foreign key.

| **Action**              | **What happens to child rows?**                                                                      | **Use Case Example**                                                           |
| ----------------------- | ---------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| **NO ACTION (Default)** | **Blocks the delete.** Throws an error at the end of the transaction if a child still references it. | Standard safe default for most relational data.                                |
| **RESTRICT**            | **Blocks the delete immediately**. Does not allow deferred transaction checks.                       | Preventing deletion of a `Product` Category if items are listed under it.      |
| **CASCADE**             | **Deletes child rows automatically** when the parent row is deleted.                                 | Deleting a `User` automatically deletes their temporary `Sessions`.            |
| **SET NULL**            | **Sets the foreign key column to `NULL`** in the child rows.                                         | Deleting an `Author` but keeping their `Books` in the database as "Anonymous". |
| **SET DEFAULT**         | **Sets the foreign key column to its default value**.                                                | Reassigning a `Task` to a fallback "Unassigned" account id.                    |

---

## Code Examples

### 1. Automatic Cleanup (`ON DELETE CASCADE`)

Use this when child data should not exist without the parent.

```sql

CREATE TABLE users (
    user_id GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(100)
);

CREATE TABLE profiles (
    profile_id GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
    bio TEXT
);

-- Deleting the user will automatically delete their profile
DELETE FROM users WHERE user_id = 1;

```

### 2. Keep the Child, Orphan the Relationship (`ON DELETE SET NULL`)

Use this when you want to preserve the historical child records.

```sql

CREATE TABLE products (
    product_id GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(100)
);

CREATE TABLE order_items (
    item_id GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_id INT REFERENCES products(product_id) ON DELETE SET NULL,
    quantity INT
);

-- Deleting the product changes order_items.product_id to NULL
DELETE FROM products WHERE product_id = 42;

```

---

## How to Modify an Existing Constraint

If you already have a table and want to add or change a delete action, you must **drop the existing constraint first** and then add the new one.

```sql

-- 1. Remove the old constraint (you must know its name)
ALTER TABLE order_items
DROP CONSTRAINT fk_order_items_products;

-- 2. Add the new constraint with the preferred ON DELETE action
ALTER TABLE order_items
ADD CONSTRAINT fk_order_items_products
FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE;

```

_Tip: If you do not know the constraint name, run `\d child_table_name` in psql to find it._
