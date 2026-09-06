# `?` AS a QUANTIFIER, MODIFIER, LOOK-AROUNDS and NON-CAPTURING-GROUPS

In a regular expression (regex), the question mark `?` serves two main purposes depending on where it is placed: **it either means "optional" (0 or 1 time) or it changes a match from "greedy" to "lazy" (non-greedy)**.

## 1. The Standard Quantifier: "Optional" (0 or 1 time)

When placed directly after a character or a group, `?` makes that item optional. It means the preceding element can appear **zero or one time**.

- **Example:** `colou?r`
  - Matches: `color` (0 occurrences of 'u')
  - Matches: `colour` (1 occurrence of 'u') [3, 4]
- **Example with a group:** Feb(ruary)?
  - Matches: `Feb`
  - Matches: `February`

## 2. The Modifier: "Lazy" / "Non-Greedy" Matching

By default, regex quantifiers like `*` (0 or more) and `+` (1 or more) are **greedy**—they try to match as much text as possible.

When you place a `?` after another quantifier (like `*?` or `+?`), it turns it into a **lazy quantifier**, meaning it will stop at the very first possible match.

| **Regex Type** | **Pattern**      | **Text**                                              | **What it matches**                                 | **Why?**                                                         |
| -------------- | ---------------- | ----------------------------------------------------- | --------------------------------------------------- | ---------------------------------------------------------------- |
| **Greedy**     | `<div>.*</div>`  | `<div>First</div><div>Second</div>`                   | `<div>First</div><div>Second</div>`                 | It grabs everything from the first `<div>` to the last `</div>`. |
| **Lazy**       | `<div>.*?</div>` | `<div>First</div><div>Second</div>`                   | `<div>First</div>`                                  | The `?` forces it to stop at the _first_ `</div>` it finds.      |
| **Greedy**     | `CAT.+?END`      | `"CAT food is fine. END But dog food is better. END"` | `CAT food is fine. END But dog food is better. END` | It grabs everything from first `CAT` to the last `END`           |
| **Lazy**       | `CAT.+END`       | `CAT food is fine. END But dog food is better. END`   | `CAT food is fine. END`                             | The `?` forces it to stop at _first_ `END` it finds.             |

## 3. Special Advanced Uses (Lookarounds and Non-Capturing Groups)

If you see `?` at the very beginning of a parenthesis block, it is being used to define special regex constructs rather than acting as a quantifier:

- **`(?:...)` Non-capturing group:** Groups characters together without saving the match for later use.
- **`(?=...)` Positive lookahead:** Ensures a specific pattern follows, without actually including it in the match.
- **`(?!...)` Negative lookahead:** Ensures a specific pattern does not follow.

---

## What if you want to match an actual question mark?

Because `?` is a special metacharacter, you must **escape it with a backslash** (`\?`) if you want to search for a literal "?" in your text. [6]

- **Example:** `is this it\?`
  - Matches: `is this it?`
