## Branch Naming Convention

branches should be named using **`lowercase letters, hyphens (-), and forward slashes (/) to categorize the work`**. The standard format is `user/category/short-description`.

| **Category**                  | **Purpose**                                            | **Example**                                         |
| ----------------------------- | ------------------------------------------------------ | --------------------------------------------------- |
| **`feature/`** or **`feat/`** | Adding new functionality or code.                      | `john/feature/django-stubs` or `john/feat/mypy-fix` |
| **`bugfix/`** or **`fix/`**   | Fixing broken code, syntax errors, or failing tests.   | `john/bugfix/mypy-import-error`                     |
| **`chore/`**                  | Updating configs, dependencies, or `.gitignore` files. | `john/chore/add-django-stubs`                       |
| **`docs/`**                   | Changing documentation or the `README.md` file.        | `docs/update-onboarding-guide`                      |

---

## Commit Message Convention (Conventional Commits)

This matches the branch names and structures messages so they are clean, readable, and can even be parsed by automated changelog tools.

### The Standard Format:

```text
type(scope): short description in present tense
```

- **`type`:** The category of the change (e.g., `feat`, `fix`, `chore`, `docs`).
- **`scope`** _(Optional)_: The part of the app affected wrapped in parentheses (e.g., `deps`, `auth`, `ci`).
- **`description`:** A short, lowercase summary starting with an imperative verb (e.g., "add", "fix", "update", not "added" or "fixing").

### Examples:

- `chore(deps): add django-stubs for mypy type checking`
- `fix(ci): silence mypy import-untyped warnings for django`
- `chore(mypy): update pyproject.toml to ignore missing imports`
- `chore(devcontainer): add prettier extension for automated formatting`
- `docs(git): add documentation for git naming standards`

---

## Putting It All Together (Your Terminal Commands)

Run this sequence to cleanly implement, name, and push your changes:

```bash

# 1. Switch back to your local development branch and pull updates
git checkout development
git pull origin development

# 2. Create your newly formatted feature branch
git checkout -b chore/add-django-stubs

# 3. Make your changes (add django-stubs via uv, or edit pyproject.toml)

# 4. Stage and commit using conventional commit syntax
git add .
git commit -m "chore(deps): add django-stubs to resolve mypy error"

# 5. Push using the -u flag to link it to GitHub
git push -u origin chore/add-django-stubs

# 6. Raise PR request against development branch

```
