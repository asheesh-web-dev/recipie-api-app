# Conditionally Unique columns / Partial Unique Index

To make a column conditionally unique, you must use a **Partial Unique Index** instead of a standard unique constraint.

PostgreSQL unique constraints cannot accept conditions, but a unique index can use a `WHERE` clause to enforce uniqueness on a specific subset of data.

---

## Method 1: The Partial Unique Index (Standard Way)

This is the most common approach. It applies the uniqueness rule only to rows that meet your `WHERE` condition.

### Scenario: Only one "Active" subscription per user

A user can have many cancelled subscriptions, but only **one active** subscription at a time.

```sql
CREATE UNIQUE INDEX idx_one_active_sub_per_user 
ON subscriptions (user_id) 
WHERE status = 'active';
```

#### How it works:

- Inserting multiple rows with `status = 'cancelled'` for the same `user_id` is allowed.
- Inserting a second row with `status = 'active'` for the same `user_id` will fail.

---

## Method 2: Conditional Uniqueness Excluding Deleted Rows (Soft Deletes)

If your application marks data as deleted using a timestamp or boolean rather than purging it from the database, you still want active entries to remain unique.

### Scenario: Active usernames must be unique, ignored if soft-deleted

```sql
CREATE UNIQUE INDEX idx_unique_active_username 
ON users (username) 
WHERE deleted_at IS NULL; -- Or WHERE is_deleted = false
```

#### How it works:

- If `user123` is soft-deleted, another person can register as `user123`.
- If a third person tries to register as `user123` while the second one is still active, PostgreSQL blocks it.

---

## Method 3: Multi-Column Conditional Uniqueness

You can combine multiple columns with a condition to create complex business rules.

## Scenario: A manager can only lead one project per department

```sql
CREATE UNIQUE INDEX idx_one_project_per_mgr_dept 
ON projects (manager_id, department_id) 
WHERE status != 'completed';
```

---

## Key Differences to Keep in Mind

| **Feature**             | **Standard Unique Constraint**     | **Partial Unique Index**                               |
| ------------------- | ------------------------------ | -------------------------------------------------- |
| **Syntax**              | `ALTER TABLE ... ADD CONSTRAINT` | `CREATE UNIQUE INDEX ... WHERE`                     |
| **Supports `WHERE`?**     | No                             | Yes                                                |
| **Foreign Key Target?** | Yes                            | No (Foreign keys cannot reference partial indexes) |
| **Performance**         | Indexes the entire table       | Indexes only the matching rows (saves disk space)  |

