# `...` [Ellipsis] as deafault argument

When you write a function in Python, you often want to set a default value for arguments. Usually, developers use `None`.

However, a problem arises if `None` is actually a **valid choice** that the user might want to pass on purpose. You lose the ability to tell if the user explicitly passed `None`, or if they skipped the argument entirely.

Because `...` (Ellipsis) is a completely unique object in Python, you can use it to solve this exact dilemma.

## The Problem: Using `None` as a Default

Imagine a function that updates a user's profile in a database.

- If they pass a string, you update the bio.
- If they pass `None`, you want to clear/delete the bio.
- If they don't pass the argument at all, you leave the bio completely untouched.

If you use `None` as the default, you cannot differentiate between the last two actions:

```python
def update_profile(username, bio=None):
    if bio is None:
        # Was this skipped, or does the user want to delete their bio? # You can't tell!
        print("Defaulting to None... but what did the user want?")

```

## The Solution: Using `...` as a Sentinel

By setting the default value to `...`, you create a foolproof separation:

```python

def update_profile(username, bio=...):
    if bio is ...:
        print("Action: Do nothing. The user skipped this argument.")

    elif bio is None:
        print("Action: Delete the bio from the database.")

    else:
        print(f"Action: Update the bio to: '{bio}'")

# Test Case 1: User skips the argument entirely
update_profile("alice")
# Output: Action: Do nothing. The user skipped this argument.

# Test Case 2: User explicitly wants to clear it
update_profile("bob", bio=None)
# Output: Action: Delete the bio from the database.

# Test Case 3: User provides data
update_profile("charlie", bio="Hello world!")
# Output: Update the bio to: 'Hello world!'

```

## Why does this work?

It works because of Python's memory management. The ellipsis `...` is a **singleton**. This means no matter where or how many times `...` is used in a program, it always points to the exact same single object in memory.

Using the `is` operator checks memory identity. Therefore, `bio is ...` will strictly evaluate to `True` only if the argument was completely omitted by the caller.
