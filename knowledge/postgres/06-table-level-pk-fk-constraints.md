# TABLE LEVEL `PRIMARY KEY` AND `FOREIGN KEY` CONSTRAINTS

In PostgreSQL, you can add table-level primary key and foreign key constraints **either during table creation using `CREATE TABLE` or by modifying an existing table using `ALTER TABLE`**. Table-level constraints are defined separately from individual columns, which is particularly useful for creating composite keys (keys made of multiple columns).

---

## 1. During Table Creation (`CREATE TABLE`)

When defining table-level constraints, you place them at the bottom of your column definition list, separated by commas.

```sql

-- Parent Table
CREATE TABLE departments (
    dept_id INT GENERATED ALWAYS AS IDENTITY,
    dept_name VARCHAR(50),
    -- Table-level Primary Key
    CONSTRAINT pk_departments PRIMARY KEY (dept_id)
);

-- Child Table
CREATE TABLE employees (
    emp_id INT GENERATED ALWAYS AS IDENTITY,
    emp_name VARCHAR(100),
    department_id INT,
    -- Table-level Primary Key
    CONSTRAINT pk_employees PRIMARY KEY (emp_id),
    -- Table-level Foreign Key
    CONSTRAINT fk_employee_department FOREIGN KEY (department_id)
        REFERENCES departments (dept_id)
        ON DELETE SET NULL
);

```

_Note: placing parentheses around the primary key column name `(dept_id)` foreign key column name `(product_id)` is **strictly compulsory** in PostgreSQL._

If you omit the brackets, PostgreSQL will throw a syntax error and reject the command.

**Why brackets are mandatory?**

1. **Databases support composite keys:**
   1. Foreign keys can link multiple columns at the same time. PostgreSQL uses the brackets to group these columns together as a single unit.
   2. For example, if a table uses a combined pair of values (like `store_id` and `item_id`) to identify a row, the brackets allow you to pass them both together:

      ```sql
      FOREIGN KEY (store_id, item_id) REFERENCES inventory(store_id, item_id)
      ```

      Even if you are only referencing a single column, PostgreSQL requires the exact same structure to understand where your column list begins and ends.

2. **SQL Parser requirement**
   1. Database engines read your commands using rigid structural rules. The `FOREIGN KEY` keyword signals to the database engine that a column list is coming next. The opening bracket `(` acts as a structural boundary telling the database parser: _"Start reading column names here,"_ and the closing bracket `)` tells it _"Stop reading column names."_
   2. Without those boundaries, the system cannot reliably separate the column name from the rest of the command clauses like `REFERENCES`.

---

## 2. Modifying an Existing Table (`ALTER TABLE`)

If your tables already exist in the database, you can add the constraints using the `ALTER TABLE` command.

### Add Table-Level Primary Key:

```sql

ALTER TABLE employees
ADD CONSTRAINT pk_employees PRIMARY KEY (emp_id);

```

### Add Table-Level Foreign Key:

```sql

ALTER TABLE employees
ADD CONSTRAINT fk_employee_department FOREIGN KEY (department_id)
    REFERENCES departments (dept_id)
    ON DELETE CASCADE;

```

---

## 3. Creating Composite Keys (Multiple Columns)

The main benefit of table-level syntax is the ability to define composite keys, which is impossible to do at the inline column level.

```sql

CREATE TABLE order_items (
    order_id INT,
    item_id INT,
    product_name VARCHAR(100),
    -- Composite Primary Key (both columns together form the unique key)
    CONSTRAINT pk_order_items PRIMARY KEY (order_id, item_id),
    -- Composite Foreign Key (references a composite key in a parent table)
    CONSTRAINT fk_order_items_order FOREIGN KEY (order_id)
        REFERENCES orders (id)
);

```

### 💡 Syntax Breakdown

- **`CONSTRAINT constraint_name`:** _Optional_ but highly recommended. It assigns a custom name to your constraint, making it much easier to drop or debug if an error occurs.
- **`FOREIGN KEY (local_column)`:** Specifies the column(s) in the current table that act as the link.
- **`REFERENCES parent_table (parent_column)`:** Points to the target table and its primary key.
- **`ON DELETE CASCADE / SET NULL`:** Optional referential actions that tell PostgreSQL what to do with the child row if the parent row is deleted.

### writing the `CONSTRAINT` keyword is not mandatory.

If you omit it, PostgreSQL will automatically generate a unique, default name for the constraint behind the scenes.

Here is how you can write them without the `CONSTRAINT` keyword:

#### 1. During Table Creation (`CREATE TABLE`)

You can jump straight to the constraint type (`PRIMARY KEY` or `FOREIGN KEY`) at the bottom of your table definition.

```sql

CREATE TABLE employees (
    emp_id INT ALWAYS GENERATED AS IDENTITY,
    emp_name VARCHAR(100),
    department_id INT,

    -- No 'CONSTRAINT' keyword or name needed
    PRIMARY KEY (emp_id),
    FOREIGN KEY (department_id) REFERENCES departments (dept_id)
);

```

#### 2. Modifying an Existing Table (`ALTER TABLE`)

Similarly, you can add them directly to an existing table.

```sql

-- Add Primary Key without a custom name
ALTER TABLE employees ADD PRIMARY KEY (emp_id);

-- Add Foreign Key without a custom name
ALTER TABLE employees ADD FOREIGN KEY (department_id) REFERENCES departments (dept_id);

```

#### 3. How PostgreSQL Names Them Automatically

PostgreSQL builds the automatic name using the **table name**, the **column name(s)**, and a suffix that describes the type of constraint.

| **Constraint Type**  | **Suffix** | **Example Auto-Generated Name** |
| -------------------- | ---------- | ------------------------------- |
| **Primary Key**      | `_pkey`    | `employees_pkey`                |
| **Foreign Key**      | `_fkey`    | `employees_department_id_fkey`  |
| **Unique Key**       | `_key`     | `employees_email_key`           |
| **Check Constraint** | `_check`   | `employees_salary_check`        |

#### 4. ⚠️ Why you should usually include it anyway

While leaving it out saves typing time, explicitly naming your constraints is a database best practice for two major reasons:

- **Easier Troubleshooting:** If a query fails because of a foreign key violation, PostgreSQL will print the exact constraint name in the error message. A name like `fk_employee_department` instantly tells you what went wrong, whereas a generated name like `employees_department_id_fkey` can be harder to parse in complex systems.
- **Simpler Modifications:** If you ever need to remove or change the constraint later, you must know its name to drop it.

```sql

-- Easy to drop when you named it:
ALTER TABLE employees DROP CONSTRAINT fk_employee_department;

-- Annoying to drop if auto-generated (you have to look up what PostgreSQL named it first)
ALTER TABLE employees DROP CONSTRAINT employees_department_id_fkey;

```
