# Foreign Key(FK)

**A Foreign Key (FK)** is a **database rule that links two tables together**. It ensures **referential** integrity, meaning it prevents you from entering data into one table that does not exist in another, preventing "orphan" records.

Think of it as a pointer: a column in a **child table** points directly to a unique column (usually the Primary Key) in a **parent table**.

---

## How It Works (A Visual Example)

Imagine an e-commerce database with a `customer`s table and an `orders` table.


```text
CUSTOMERS Table (Parent)
+-------------+---------------+

| customer_id | customer_name |
+-------------+---------------+

|    1        | Alice         |
|    2        | Bob           |
+-------------+---------------+
     ▲
     │ (The Foreign Key Link)
     │
 ORDERS Table (Child)
+----------+-------------+------------+

| order_id | customer_id | order_date |
+----------+-------------+------------+

| 101 | 1 | 2026-08-15 | -> Allowed (Alice exists)
| 102 | 3 | 2026-08-16 | -> BLOCKED! (Customer 3 doesn't exist)
+----------+-------------+------------+
```
---

## Standard Foreign Key Syntax

Here is how you write it in SQL. The child table uses `REFERENCES` to point to the parent.

```sql
-- 1. The Parent Table
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL
);
-- 2. The Child Table
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    order_date DATE NOT NULL,
    customer_id INT,

    -- Defining the Foreign Key
    CONSTRAINT fk_customer
        FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id)

);
```

---

## Strict Rules Enforced by Foreign Keys

Once a Foreign Key is active, PostgreSQL strictly enforces three rules:

1. **No Ghost Inserts:** You cannot insert an order for `customer_id = 99` if customer 99 does not exist in the parent table.
2. **No Orphan Updates:** You cannot change an order's `customer_id` to a value that doesn't exist.
3. **Restricted Deletions:** You cannot delete Alice from the `customers` table if she still has orders attached to her in the `orders` table. PostgreSQL will throw an error to protect the data.

---

## Handling Parent Deletions (ON DELETE Actions)

What _should_ happen to the child rows if a parent row is deleted? You can customize this behavior using `ON DELETE` clauses:

- **`ON DELETE RESTRICT` / `NO ACTION` (Default):** Blocks you from deleting the parent row if child rows exist.
- **`ON DELETE CASCADE`:** Automatically deletes all child rows when the parent row is deleted. (e.g., Delete a customer -> automatically delete all their orders).
- **`ON DELETE SET NULL`:** Sets the foreign key column in the child rows to `NULL` when the parent row is deleted. (e.g., Delete a customer -> keep the orders, but set customer_id to blank).

## Example using CASCADE:

```sql
CREATE TABLE orders (
order_id SERIAL PRIMARY KEY,
customer_id INT REFERENCES customers(customer_id) ON DELETE CASCADE
);
```

---

## Core Requirements for a Foreign Key

To make a column a Foreign Key, it must meet these criteria:

- **Target Must Be Unique:** The targeted column in the parent table must have a _PRIMARY KEY_ or _UNIQUE_ constraint.
- **Matching Data Types:** The column in the child table must be the exact same data type as the column in the parent table (e.g., both must be `INT`, or both must be `UUID`).
