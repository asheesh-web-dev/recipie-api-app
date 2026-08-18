# `UNIQUE` Constraint

A PostgreSQL unique constraint is a **database rule ensuring that all values in a column, or a group of columns, are completely distinct across every row in a table**.

## How PostgreSQL Creates and Enforces It

When you define a unique constraint, PostgreSQL does not manually scan the entire table sequential row-by-row on every insertion. Instead, it handles it via the following mechanism: [3]

- **Automatic B-Tree Index Generation:** The moment a unique constraint is defined, PostgreSQL automatically creates a **hidden, unique B-tree index** on the specified columns.
- **The Index is the Enforcer:** This underlying index is what actually prevents duplicate entries. When you try to insert or update data, PostgreSQL checks this high-performance B-tree index to see if the value already exists.
- **No Redundant Indexes:** Because PostgreSQL automatically generates this index, you do not need to manually create an index on columns assigned a unique constraint. Doing so would waste storage space and slow down write operations.

---

## How to Create Unique Constraints

You can define a unique constraint in three different ways depending on your schema requirements:

## 1. Single-Column Level

Best when a single field (like an email or username) must be unique.

```sql,
CREATE TABLE users (
  user_id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE -- Automatically creates a unique index
);
```
## 2. Multi-Column Table Level

Used when individual columns can repeat, but their combined value must be completely unique.

```sql
CREATE TABLE course_enrollments (
  student_id INT,
  course_id INT,
  UNIQUE (student_id, course_id) -- The paired combination must be unique
);
```
## 3. Altering an Existing Table

If you already have a table populated with data, you can append the constraint after verifying no duplicates exist.

```sql
ALTER TABLE users ADD CONSTRAINT unique_username UNIQUE (username);
```

---

## Behavior with NULL Values

Handling missing data follows specific rules within unique constraints:

- **NULLs are Distinct (Default):** By default, PostgreSQL treats `NULL` values as completely distinct / unknown. This means you can insert multiple rows with `NULL` into a unique column because `NULL` never equals another `NULL`. _you can't compare two unknowns_.
- **NULLs Not Distinct:** If your business logic dictates that you should only ever have one missing/empty entry, you can declare `NULLS NOT DISTINCT`.

    ```sql
    CREATE TABLE profiles (
    profile_id INT,
    phone_number VARCHAR(15),
    UNIQUE NULLS NOT DISTINCT (phone_number) -- Allows exactly ONE null value
    );
    ```

---

## Unique Constraints vs. Unique Indexes

While PostgreSQL uses unique indexes to build unique constraints under the hood, they serve slightly different purposes in practice:

| **Feature**            | **Unique Constraint**                                           | **Unique Index**                                              |
| ------------------ | ----------------------------------------------------------- | --------------------------------------------------------- |
| **Primary Purpose**    | Enforces a relational data integrity rule.                  | Maximizes query performance and search speeds.            |
| **Database Schema**    | Acts as an explicit architectural object in your table DDL. | Serves as a physical storage structure behind the scenes. |
| **Partial Conditions** | Cannot be applied to filtered subsets of data.              | Supports conditions (e.g., `WHERE status = 'active'`).      |

If your primary objective is strictly performance or specialized indexing (like a partial index), build a **Unique Index**. If your objective is structural data validity, lean on a **Unique Constraint**.


