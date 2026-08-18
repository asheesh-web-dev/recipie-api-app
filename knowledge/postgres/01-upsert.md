# postgresql upsert [update or insert]

An **upsert** in PostgreSQL is an **operation that inserts a new row or updates the existing row if a duplicate key conflict occurs**. You do this using the `INSERT ... ON CONFLICT` command. It keeps your data safe and clean.

## How ON CONFLICT Works

The `ON CONFLICT` clause tells Postgres what to do when a **unique index** or **primary key** _constraint is violated_.

- **Conflict Target:** You tell Postgres which column to watch for duplicate values (like a **unique ID** or **email**).
- **Conflict Action:** You tell Postgres to either do nothing (`DO NOTHING`) or update the old data (`DO UPDATE SET`).

## Conflict Resolution Steps

Postgres handles the conflict in a clear order:

- **Check Constraints:** Postgres tries to run a normal insert statement.
- **Detect Violation:** If a row already exists with the same _unique key or primary key, a conflict error is raised_.
- **Intercept Error:** Instead of failing, the `ON CONFLICT` block stops the error.
- **Apply Action:**
    - If you chose `DO NOTHING`, Postgres skips the insert and _keeps the old row safe_.
    - If you chose `DO UPDATE SET`, Postgres runs an **update command** on the old row using `EXCLUDED.column_name` to grab the new values you tried to insert.

## General Syntax Structure

```sql
INSERT INTO table_name (column1, column2) 
VALUES (value1, value2)
ON CONFLICT (conflict_target) 
DO ACTION;
```
---

## Option 1: The `DO NOTHING` Syntax

Use this when you want to ignore the new data if a duplicate already exists.

```sql
INSERT INTO users (id, email, name)
VALUES (1, 'alex@example.com', 'Alex')
ON CONFLICT (id) 
DO NOTHING;
```

- **`(id)`:** The conflict target (the primary key or unique column).
- **`DO NOTHING`:** Tells Postgres to skip the insert safely without throwing an error.

---

## Option 2: The `DO UPDATE` Syntax

Use this when you want to overwrite the old data with the new data. You use the special `EXCLUDED` table to reference the new values you tried to insert.

```sql
INSERT INTO users (id, email, name)
VALUES (1, 'alex_new@example.com', 'Alex Jones')
ON CONFLICT (id) 
DO UPDATE SET
  email = EXCLUDED.email,
  name = EXCLUDED.name;
```

- **`EXCLUDED.email`:** Refers to `'alex_new@example.com'` (the new value you attempted to insert).
- **`email =`:** The existing row column that gets updated.

---

## Advanced: Conditional Upsert Syntax

You can add a WHERE clause to the update section. This ensures the update only happens if specific conditions are met.

```sql
INSERT INTO users (id, email, login_count)
VALUES (1, 'alex@example.com', 10)
ON CONFLICT (id) 
DO UPDATE SET
  login_count = EXCLUDED.login_count
WHERE EXCLUDED.login_count > users.login_count;
```

- **`users.login_count`:** Refers to the current value already stored in the table.
- **Result:** The row only updates if the new login count is higher than the old one.

