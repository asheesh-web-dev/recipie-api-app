# taking backup using `pg_dump` and restoring using `pg_restore`

## `pg_dump` and `pg_restore`

In PostgreSQL, `pg_dump` and `pg_restore` are the **official, standard tools used for Logical Backups**. They work by extracting your database structure (schema) and data into a file, which can later be used to rebuild the database from scratch.

## Think of `pg_dump` as the **packer** that boxes up your database, and `pg_restore` as the **unpacker** that sets it back up.

### 1. `pg_dump` (The Backup Tool)

`pg_dump` is a command-line utility that creates a backup of a **single** PostgreSQL database. A massive benefit of `pg_dump` is that it is completely **non-blocking**; users can continue reading and writing to the database while the backup is running.

`pg_dump` can output backups in a few different styles (called formats).

#### Format A: Plain Text Script (`.sql`)

- **What it is:** A standard SQL text file containing `CREATE TABLE` and `INSERT` commands.

- **How to run it:**

  ```bash
  pg_dump -U username -d my_database > backup.sql
  ```

- **How to restore it:** You cannot use `pg_restore` for plain text files. Instead, you use the standard PostgreSQL query tool, `psql`:

  ```bash
  psql -U username -d new_database -f backup.sql
  ```

#### Format B: Custom/Directory Format (`.dump` or `.tar`) — _Recommended_

- **What it is:** A compressed, custom binary format. It is much smaller than a plain text file.
- **Why it's better:** It allows for faster, parallel (multi-threaded) restores and lets you selectively restore only specific tables rather than the whole database.
- **How to run it:**

  ```bash

  # -F c means Format = Custom
  pg_dump -U username -F c -d my_database -f backup.dump

  ```

---

### 2. `pg_restore` (The Restore Tool)

`pg_restore` is a command-line utility used **exclusively** to restore backups created by `pg_dump` in its non-plain-text formats (like the Custom or Directory formats).

It reads the compressed backup file and reconstructs the database onto a target server.

#### Basic Restore Command:

```bash
pg_restore -U username -d target_database backup.dump
```

#### Advanced Powers of `pg_restore`:

Because custom format backups contain a structural map of your database, `pg_restore` gives you incredible control during recovery:

- **High-Speed Parallel Processing (`-j`):** If your database is large and your server has multiple CPU cores, you can run the restore across multiple threads simultaneously to drastically cut down download times.

  ```bash
  # Runs the restore using 4 CPU cores at once
  pg_restore -U username -d target_database -j 4 backup.dump
  ```

- **Restore a Single Table (`-t`):** If a bug or a developer accidentally deleted data from just one table, you don't need to restore the whole database. You can pull a single table out of the backup file.

  ```bash
  pg_restore -U username -d target_database -t employees backup.dump
  ```

---

### 💡 How they handle identity sequences automatically

[Tying back to our earlier conversation about GENERATED ALWAYS AS IDENTITY](./07-serial-vs-identity-columns.md#question-4-so-if-i-am-using-generated-always-as-identity-i-cant-migrate-the-data): When `pg_dump` processes an identity column, it writes the exact schema rules and appends a special sequence set command at the very end of the file (using internal catalog calls similar to `setval`).

When `pg_restore` executes that backup on a new server, it safely pushes the records in and automatically jumps the internal sequence counters to match the highest migrated ID. You do not need to write `OVERRIDING SYSTEM VALUE` or manually sync anything; these tools handle it all natively.

---

---

## Question-1? is `pg_backup` takes backup of all tables inside single database or it can take backup of database name as well? can it take backup of all the databases present in server or there are different tools for that?

By default, `pg_dump` only backs up **one specific database at a time**, and you do have to create the empty target database manually before running `pg_restore`.

However, PostgreSQL provides options and companion tools to automate the creation of databases during restoration so you don't have to do it manually.

Here is exactly how it works based on the commands you use:

---

### Scenario 1: The Default Behavior (You provide the database)

If you run the standard `pg_dump` command, it only extracts the tables, schemas, and data inside that _single_ database. It does **not** include the command to create the database itself.

During restoration, your process looks like this:

1. You manually connect to your new server and run: `CREATE DATABASE new_db;`
2. You run `pg_restore` or `psql` and explicitly tell it to point to `new_db`.

---

### Scenario 2: The Automatic Switch (`--create`)

If you want the backup file to **automatically create the database** for you on the new server, you must add the `--create` (or `-C`) flag when taking the backup or during the restore.

```bash
# Taking the backup with the create flag
pg_dump -U username -F c -C -d old_db -f backup.dump
```

When you run `pg_restore` with this file, it will:

1. Connect to the new server's master template database (usually called `postgres`).
2. Read the backup file, see the instruction to build a database, and execute `CREATE DATABASE old_db;` automatically.
3. Switch its connection inside the script and load all the tables into that newly created database.

---

### Scenario 3: Backing Up the ENTIRE Server (`pg_dumpall`)

If you have a server with **multiple databases** (e.g., `production_db`, `testing_db`, `analytics_db`) along with global settings like user passwords and roles, `pg_dump` cannot handle it.

Instead, you use a different, companion tool called pg_dumpall.

- **What it does:** It loops through every single database on your server, extracts all their tables, and copies all global user roles and permissions.
- **How it handles restoration:** It always outputs as a plain text `.sql` file. This file automatically contains `CREATE ROLE` and `CREATE DATABASE` commands for every single database on the original server.
- **How to restore it**: You point it at a completely blank, freshly installed PostgreSQL server using `psql`, and it will automatically recreate your entire database cluster exactly as it was.

  ```bash
  psql -U username -f full_cluster_backup.sql
  ```

---

### Summary Checklist

- `pg_dump` = Backs up **one** database. By default, you must create the target database first, _unless_ you use the `--create` flag.
- `pg_dumpall` = Backs up **all** databases on the server at once and automatically creates them all during restoration.
