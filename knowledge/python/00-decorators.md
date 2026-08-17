# decorators

**Decorators** in let you modify or extend the behavior of a function or class **without changing its original code**.

The key idea is:

> A decorator is a function that takes another function as input and returns a new function.

## 1. Start without decorators

Suppose we have:

```python
def greet(name: str) -> str:
    return f"Hello, {name}!"

print(greet("Alice"))
```

Output:

```text
Hello, Alice!
```

Now imagine we want to print something before and after `greet()` runs.

We could manually do:

```python
def greet(name: str) -> str:
    print("Before")
    result = f"Hello, {name}!"
    print("After")
    return result
```

But this mixes the **actual business logic** with extra behavior.

A decorator lets us separate them.

---

## 2. Creating a simple decorator

```python
from typing import Callable, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def my_decorator(func: Callable[P, R]) -> Callable[P, R]:
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        print("Before")

        result = func(*args, **kwargs)

        print("After")
        return result

    return wrapper
```

Now use it:

```python
@my_decorator
def greet(name: str) -> str:
    return f"Hello, {name}!"
```

When Python sees:

```python
@my_decorator
def greet(name: str) -> str:
    ...
```

it essentially does:

```python
greet = my_decorator(greet)
```

So `greet` is replaced by the `wrapper` function.

Calling:

```python
greet("Alice")
```

is therefore roughly equivalent to:

```python
wrapper("Alice")
```

and the wrapper calls the original `greet()` internally.

---

## 3. Understanding `*args` and `**kwargs`

This is important for decorators.

Consider:

```python
def add(a: int, b: int) -> int:
    return a + b
```

and:

```python
def multiply(a: int, b: int) -> int:
    return a * b
```

Our decorator should ideally work with **both** functions.

That's why we write:

```python
def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
    ...
```

`*args` collects positional arguments:

```python
add(10, 20)
```

becomes approximately:

```python
args = (10, 20)
```

`**kwargs` collects keyword arguments:

```python
add(a=10, b=20)
```

becomes:

```python
kwargs = {
    "a": 10,
    "b": 20
}
```

Then:

```python
func(*args: P.args, **kwargs: P.kwargs)
```

passes them back to the original function.

---

## 4. A practical example: timing a function

Decorators are commonly used for logging, timing, authentication, caching, etc.

For example:

```python
import time
from typing import Callable, ParamSpec, TypeVar


P = ParamSpec("P")
R = TypeVar("R")

def timer(func: Callable[P, R]) -> Callable[P, R]:
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        start = time.perf_counter()

        result = func(*args, **kwargs)

        end = time.perf_counter()

        print(f"{func.__name__} took {end - start:.4f} seconds")

        return result

    return wrapper
```

Use it:

```python
@timer
def slow_function() -> str:
    time.sleep(1)
    return "Done"
```

Then:

```python
result = slow_function()
print(result)
```

You might get:

```text
slow_function took 1.0012 seconds
Done
```

The important part is that `slow_function()` itself doesn't contain any timing code.

The decorator adds that behavior.

---

## 5. `functools.wraps`

There's one problem with our decorator.

Consider:

```python
def timer(func: Callable[P, R]) -> Callable[P, R]:
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        return func(*args, **kwargs)

    return wrapper
```

After decorating:

```python
@timer
def greet(name: str) -> str:
    """Greet a person."""
    return f"Hello, {name}!"
```

Python now sees `greet` as `wrapper`.

So:

```python
print(greet.__name__)
```

gives:

```text
wrapper
```

That's undesirable.

Use `functools.wraps`:

```python
from functools import wraps
from typing import Callable, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")

def timer(func: Callable[P, R]) -> Callable[P, R]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        return func(*args, **kwargs)

    return wrapper
```

Now Python preserves metadata such as:

```python
greet.__name__
greet.__doc__
```

So **`@wraps(func)` is a best practice when writing decorators.**

---

## 6. explaining type hints

For modern Python, you can use `ParamSpec` and `TypeVar`.

```python
from functools import wraps
from typing import Callable, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def logger(func: Callable[P, R]) -> Callable[P, R]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        print(f"Calling {func.__name__}")

        result = func(*args, **kwargs)

        print(f"Finished {func.__name__}")

        return result

    return wrapper
```

Now:

```python
@logger
def add(a: int, b: int) -> int:
    return a + b
```

The type checker understands that `add` still behaves like:

```python
(int, int) -> int
```

### Why `ParamSpec`?

Think of:

```python
P = ParamSpec("P")
```

as meaning:

> "Remember the parameters of the function I'm decorating."

And:

```python
R = TypeVar("R")
```

means:

> "Remember the return type."

Therefore:

```python
Callable[P, R]
```

means:

> "A callable with parameters `P` that returns `R`."

---

## 7. Decorator that accepts its own arguments

You can also make decorators configurable.

For example:

```python
from functools import wraps
from typing import Callable, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def repeat(times: int) -> Callable[[Callable[P, R]], Callable[P, R]]:
    if times < 1:
        raise ValueError("times must be at least 1")

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            result = func(*args, **kwargs)

            for _ in range(times - 1):
                result = func(*args, **kwargs)

            return result

        return wrapper

    return decorator
```

Then:

```python
@repeat(3)
def greet(name: str) -> str:
    print(f"Hello {name}")
    return "done"
```

Calling:

```python
greet("Alice")
```

prints:

```text
Hello Alice
Hello Alice
Hello Alice
```

> > Note: It calls func() multiple times, but result gets overwritten each time. If the function returns different values,Only the last result survives.

### if we actually want all results

```python
def repeat(times: int) -> Callable[[Callable[P, R]], Callable[P, list[R]]]:
    def decorator(func: Callable[P, R]) -> Callable[P, list[R]]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> list[R]:
            results: list[R] = []

            for _ in range(times):
                result = func(*args, **kwargs)
                results.append(result)

            return results

        return wrapper

    return decorator
```

Now:

```python
@repeat(3)
def get_number() -> int:
    return random.randint(1, 100)
```

produces:

```python
[42, 17, 83]
```

Notice the two levels:

```text
repeat(3)
    ↓
decorator
    ↓
wrapper
    ↓
greet()
```

This is why decorators with arguments initially look confusing.

---

## 8. A very useful mental model

Think of a decorator like wrapping a gift 🎁.

Original function:

```text
       ┌─────────────┐
       │   greet()   │
       └─────────────┘
```

Decorator:

```text
┌─────────────────────────────┐
│        decorator            │
│                             │
│   ┌─────────────────────┐   │
│   │      greet()        │   │
│   └─────────────────────┘   │
│                             │
└─────────────────────────────┘
```

The original function is still there.

The decorator simply controls what happens **around** it.

For example:

```python
def logger(func):
    def wrapper(*args, **kwargs):
        print("START")
        result = func(*args, **kwargs)
        print("END")
        return result

    return wrapper
```

Conceptually:

```text
wrapper()
   │
   ├── START
   │
   ├── original function()
   │
   └── END
```

---

## 9. Common real-world uses

You'll see decorators everywhere in Python.

### Logging

```python
@logger
def process_data() -> None:
    ...
```

### Authentication

```python
@requires_login
def delete_account() -> None:
    ...
```

### Caching

```python
from functools import cache

@cache
def fibonacci(n: int) -> int:
    ...
```

### Timing

```python
@timer
def expensive_operation() -> None:
    ...
```

### Web frameworks

For example, frameworks use decorators to associate functions with routes:

```python
@app.get("/users")
def get_users() -> list[str]:
    return ["Alice", "Bob"]
```

Here, the decorator tells the framework:

> "When someone requests `/users`, run this function."

---

## The 4 things to remember

If you're learning decorators, focus on these:

```python
def decorator(func):
    def wrapper(*args, **kwargs):
        # before

        result = func(*args, **kwargs)

        # after
        return result

    return wrapper
```

Then:

```python
@decorator
def my_function():
    ...
```

means:

```python
my_function = decorator(my_function)
```

And for **good modern type hints**, use:

```python
from functools import wraps
from typing import Callable, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def decorator(func: Callable[P, R]) -> Callable[P, R]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        return func(*args, **kwargs)

    return wrapper
```

