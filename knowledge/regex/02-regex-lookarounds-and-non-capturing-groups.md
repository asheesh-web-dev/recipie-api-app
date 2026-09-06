# Mastering Regex Lookarounds and Non-Capturing Groups

## Lookarounds

In regular expressions, **lookaround** ( consists of **lookahead** and **lookbehind** ) **`are zero-width assertions`**. This means they **match a position rather than actual text**, allowing you to verify what comes before or after a pattern without including those characters in the final match result.

Think of lookarounds as conditions: _"Match X, but only if Y is right next to it."_

### Lookahead

**peek ahead where you are and check if you find the lookahead pattern and return back**

- **Example-1**
  - **Pattern:** `cat(?=nap)`
  - **How it works:** _The engine finds "cat" first, then peeks ahead to see if "nap" is next_.
  - **Match:** It matches "cat" in `"catnap"`, but fails in `"catfish"`.
- **Example-2:** Password Validation (atleat one upper case letter and one digit)
  - **Pattern:** `^(?=.*[A-Z])(?=.*\d).{8,}$` -
  - **How it works:**
    - The engine starts at `^` (the beginning).
    - `(?=.*[A-Z])` looks ahead across the _whole_ string to find an uppercase letter, then **returns to the beginning**.
    - `(?=.*\d)` looks ahead across the whole string to find a digit, then **returns to the beginning**.
    - Only if both lookaheads succeed does the engine move to `.{8,}`, which starts counting 8 characters from the **very beginning** of the string.
- **Example-3:** Password Validation (Atleast Two UpperCase letters)
- **Pattern:** `(?=.*[A-Z].*[A-Z])`
- **Optimization:** Instead of repeating `.*[A-Z]` twice, you can group it and tell the regex engine to look for that sequence exactly **2 times**: `(?=(?:.*[A-Z]{2}))`

---

### The 4 Types of Lookaround

| **Type**                | **Syntax** | **What it does**                            | **Example**   | **Matches**          |
| ----------------------- | ---------- | ------------------------------------------- | ------------- | -------------------- |
| **Positive Lookahead**  | `X(?=Y)`   | Matches `X` only if **followed by** `Y`     | `\d+(?= USD)` | **100** in "100 USD" |
| **Negative Lookahead**  | `X(?!Y)`   | Matches `X` only if **NOT followed by** `Y` | `\d+(?! USD)` | **100** in "100 EUR" |
| **Positive Lookbehind** | `(?<=Y)X`  | Matches `X` only if **preceded by** `Y`     | `(?<=\$)\d+`  | **50** in "$50"      |
| **Negative Lookbehind** | `(?<!Y)X`  | Matches `X` only if **NOT preceded by** `Y` | `(?<!\$)\d+`  | **50** in "€50"      |

---

### Key Concepts to Remember

- **Zero-Width/Non-Consuming:** Lookarounds inspect the string, confirm the condition, and then "give up" the match on those conditional characters. The regex cursor returns right back to where it was.
- **Flavor Limitations:** Almost all modern languages support lookaheads. However, some languages or older engines have limitations with lookbehinds, either forbidding them entirely or requiring them to have a fixed length (e.g., you cannot use variable quantifiers like `*` or `+` inside a lookbehind in languages like JavaScript or Python's standard `re` module).

### Common Use Cases

- **Password Validation:** Ensuring a password contains at least one number and one uppercase letter using multiple positive lookaheads: `^(?=.*[A-Z])(?=.*\d).{8,}$`
- **Data Extraction:** Grabbing prices or IDs without pulling the symbols or labels surrounding them.

## Non-Capturing Groups

**Non-capturing groups**, written as `(?:pattern)`, are **`used to group parts of a regular expression together without saving the matched text for later use`**.

By default, standard parentheses `(pattern)` create **capturing groups**. They tell the regex engine to remember whatever text matches inside them so you can reference it later (like using `$1` or `\1`). A non-capturing group tells the engine: _"Group these tokens together for logic, but don't waste memory or create a group index for them."_

---

### The Two Main Uses of Non-Capturing Groups

#### 1. Applying Quantifiers to a Whole Phrase

If you want to make a multi-character word or phrase optional or repeating, you must group it. Using a non-capturing group does this cleanly without polluting your match results.

- **Scenario:** You want to match "cat" or "catdogdogdog".
- **Capturing approach:** `cat(dog)*` → This works, but it unnecessarily creates "Group 1" containing the last "dog".
- **Non-capturing approach:** `cat(?:dog)*` → This groups "dog" so the `*` multiplier applies to the whole word, but **no extra groups are created**.

#### 2. Using Alternation (The OR `|` Operator)

The pipe `|` operator has very low precedence. Without grouping, `cat|dog` means "match the entire string 'cat' OR the entire string 'dog'". If you want to use the OR operator inside a longer pattern, you must isolate it.

- **Scenario:** You want to match "I love cats" or "I love dogs".
- **Incorrect:** `I love cats|dogs` → This matches "I love cats" OR just the word "dogs".
- **Capturing approach:** `I love (cats|dogs)` → This works, but it creates an unwanted "Group 1" containing either "cats" or "dogs".
- **Non-capturing approach:** `I love (?:cats|dogs)` → This correctly restricts the `|` operator without cluttering your match data.

---

### Direct Comparison

Here is how the regex engine handles the string `"ID: 123"` with both methods:

| **Feature**        | **Capturing Group: (`ID`): (`\d+`)**   | **Non-Capturing Group: (`?:ID`): (`\d+`)** |
| ------------------ | -------------------------------------- | ------------------------------------------ |
| **Full Match**     | `"ID: 123"`                            | `"ID: 123"`                                |
| **Group 1 (`$1`)** | `"ID"`                                 | `"123"`                                    |
| **Group 2 (`$2`)** | `"123"`                                | _Does not exist_                           |
| **Performance**    | Slower (allocates memory for tracking) | **Faster (cleaner execution)**             |

### When should you use them?

As a rule of thumb, **use non-capturing groups (`?:...`) by default** whenever you need to group tokens or use alternation. Only switch to capturing groups (`...`) when you actively plan to extract that specific piece of text or use it as a backreference.

---

## Examples In Python

In **Python**, regex is handled via the built-in **`re`** module.

Python fully supports both lookarounds and non-capturing groups. However, Python's lookbehinds must be of a **fixed length**—you cannot use variable-length quantifiers like `*`, `+`, or `?` inside them.

---

### 1. Lookahead and Lookbehind Example

Here is how to extract a price figure from a string without including the currency symbol ($) or currency code (USD).

```python

import re

text = "The price is $150 USD."

# Positive Lookbehind (?<=\$) matches position after '$'
# Positive Lookahead (?= USD) matches position before ' USD'
pattern = r"(?<=\$)\d+(?= USD)"

match = re.search(pattern, text)

if match:
    # Outputs '150' (The '$' and 'USD' are not part of the match)
    print(f"Matched price: {match.group(0)}")
```

### 2. Non-Capturing Group Example

Here is how you use alternation `|` to match an image filename without creating an accidental capture group for the file extension.

```python
import re

text = "Profile picture: avatar.png"

# (?:png|jpg|jpeg) cleanly groups the extensions for the OR operator
# (\w+) is a standard capturing group to extract the name
pattern = r"(\w+)\.(?:png|jpg|jpeg)"

match = re.search(pattern, text)
if match:
    # group(0) is always the full match: 'avatar.png'
    print(f"Full match: {match.group(0)}")

    # group(1) contains the first capturing group: 'avatar'
    print(f"Filename: {match.group(1)}")

    # Printing group(2) would throw an IndexError because (?:...) was ignored
```

### 3. Finding All Matches with `re.findall`

Non-capturing groups are incredibly important when using `re.findall()`. If you use a regular capturing group, `findall()` returns only the group contents instead of the whole match.

```python
import re

html = "<li>Apple</li><li>Banana</li>"

# BAD: Captures the tags unnecessarily
print(re.findall(r"(<li>.*?</li>)", html))
# Output: ['<li>Apple</li>', '<li>Banana</li>']

# BAD: If we try to group tags with standard groups, look what happens:
print(re.findall(r"(<li>)(.*?)(</li>)", html))
# Output: [('<li>', 'Apple', '</li>'), ('<li>', 'Banana', '</li>')]

# GOOD: Non-capturing groups isolate the logic while keeping findall clean
print(re.findall(r"(?:<li>)(.*?)(?:</li>)", html))
# Output: ['Apple', 'Banana']
```
