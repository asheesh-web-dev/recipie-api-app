# `__new__` and `__init__`

## understanding `__new__()` and `__init__()`

**`__new__` is the actual creator (_constructor_) that allocates memory for a new object, while `__init__` is the initializer that configures the newly created object by assigning its attributes.**

### The Execution Order

When you create an instance of a class (e.g., `obj = MyClass()`), Python invokes a built-in orchestrator (`type.__call__`) behind the scenes. The exact sequence follows this strict order:

1. **`**new**(cls, \*args, **kwargs)` runs first**. It takes the class itself as an argument (`cls`), allocates memory, and **must return** a fresh instance of that class.
2. **`**init**(self, \*args, **kwargs)`runs second.** It receives the instance returned by`**new**` as its first argument (`self`) and sets up initial variables. It must return **None**.

### Core Differences

| **Feature**         | **`__new__` Method**                            | **`__init__` Method**                                 |
| ------------------- | ----------------------------------------------- | ----------------------------------------------------- |
| **Primary Role**    | Object **Creation** (Memory allocation).        | Object **Initialization** (State configuration).      |
| **First Argument**  | Takes the class (`cls`).                        | Takes the instance (`self`).                          |
| **Return Value**    | Must return a newly created object instance.    | Must not return anything (implicitly returns `None`). |
| **Method Type**     | Implicitly a static method.                     | An instance method.                                   |
| **Usage Frequency** | Rarely overridden (only for special use cases). | Overridden in almost every custom class.              |

### Code Example: Visualization of the Flow

You can see exactly how they pass control to one another in this standard code layout:

```python

class SampleClass:
    def __new__(cls, *args, **kwargs):
        print("1. __new__ is executing: Creating the empty object container.")
        # Call the parent class (object) to allocate memory for the instance
        instance = super().__new__(cls)
        return instance

    def __init__(self, name):
        print("2. __init__ is executing: Populating the object with data.")
        self.name = name

# Triggering object instantiation
obj = SampleClass("Python")
```

#### Output:

```text
1. __new__ is executing: Creating the empty object container.
2. __init__ is executing: Populating the object with data.
```

### When to Use Which?

#### Use `__init__` for 99% of tasks:

- Setting up default instance variables.
- Accepting initial data parameters from users.
- Bootstrapping lightweight operational logic inside the object.

#### Use `__new__` only for highly advanced tasks:

- **Implementing Singletons:** Restricting a class so it only ever yields one unique instance across your entire program.
- **Subclassing Immutable Types:** Customizing built-in unchangeable types like `int`, `str`, or `tuple` (since their values cannot be safely altered inside `__init__`).
- **Metaprogramming:** Altering the behavior of object construction at the root level.

_Note: Python will only trigger `__init__` if `__new__` successfully returns an instance of that exact same class. If `__new__` returns a different object type or `None`, `__init__` will be skipped entirely._

---

---

## Question-1? so if we are not overriding the `__new__` in our class then its provided by object class as inherited method ? explain me the syntax `instance = super().__new__(cls)` ? does only the `object` have power to allocatte memory?

You are **completely correct**. If you do not override `__new__` in your Python class, it automatically inherits the `__new__` method from the base `object` class.

Ultimately, the `object.__new__` method is the one responsible for the actual memory allocation for new instances.

---

### Understanding the Syntax: `instance = super().__new__(cls)`

When you override `__new__`, you typically write this exact line. Here is the breakdown of what each part means:

- **`super()`:** Finds the next class in your class's Method Resolution Order (MRO). If you are using simple inheritance, this points directly to the base object class.
- **`.__new__`:** Calls the object creation function of that parent class.
- **`(cls)`:** Passes the current class (`cls`) as an argument. Even though `object.__new__` is doing the work, it needs to know _which_ specific blueprint (your class) it is allocating memory for.
- **`instance = `:** Captures the newly created, empty object in memory returned by the parent class.

### Does only the object class have the power to allocate memory?

At the Python level, **yes**.

1. **The Ultimate Authority:** Every standard class in Python eventually inherits from object. No matter how many custom `__new__` methods you chain together using `super()`, the final call in the chain must reach `object.__new__`.
2. **The C-Level Reality:** Under the hood, Python is written in C (CPython). `object.__new__` is a wrapper around low-level C functions (like `PyType_GenericAlloc`). These C functions talk to your operating system to reserve the physical RAM bytes.
3. **The Metaclass Exception:** The only real exception to this rule is if you write a custom **Metaclass** or a **C-extension module** that completely bypasses standard Python object creation. For 99% of Python programming, `object` is the sole gatekeeper of memory allocation.

---

### A Concrete Example

Here is how the workflow looks in code:

```python

class MyClass:
    def __new__(cls, *args, **kwargs):
        print("1. __new__ intercepting the creation process.")

        # We hand over the job to object.__new__ to actually carve out memory
        instance = super().__new__(cls)

        print("2. Memory allocated. Object exists but is empty.")
        return instance

    def __init__(self, name):
        print("3. __init__ running to populate the allocated memory.")
        self.name = name
# Triggering the process
obj = MyClass("Python")

```
