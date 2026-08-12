## Branch Naming Convention

branches should be named using **`lowercase letters, hyphens (-), and forward slashes (/) to categorize the work`**. The standard format is `user/category/short-description`.

| **Category**          | **Purpose**                                 | **Example**                                   |
| --------------------- | ------------------------------------------- | --------------------------------------------- |
| `feat/` or `feature/` | New functionality, app, or endpoint         | `feat/users-jwt-authentication`               |
| `fix/` or `bugfix/`   | Bug fixes in endpoints or logic             | `fix/orders-null-total-amount-bug`            |
| `refactor/`           | Code cleanup without functional change      | `refactor/products-optimize-queryset-queries` |
| `test/`               | Adding or updating unit/integration tests   | `test/payments-stripe-webhook-tests`          |
| `docs/`               | API documentation (Swagger/OpenAPI, README) | `docs/swagger-schema-annotations`             |
| `chore/`              | Dependencies, settings, CI/CD               | `chore/upgrade-djangorestframework-3-15`      |

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

### Allowed Types

- `feat`: A new API endpoint, serializer, view, or model.
- `fix`: A bug fix in logic, queryset, or validation.
- `refactor`: Restructuring DRF views/serializers without altering behavior.
- `perf`: Database query optimizations (`select_related`, `prefetch_related`, indexing).
- `test`: Adding API Client tests or pytest suites.
- `docs`: OpenAPI schema additions or README updates.
- `chore`: Package updates, settings tweaks.

## Examples:

| **Task**                                                | **Branch names**                                           | **Commit messages**                                                       |
| ------------------------------------------------------- | ---------------------------------------------------------- | ------------------------------------------------------------------------- |
| **Refactoring Code (No Feature Changes, No Bug Fixes)** | `refactor/cleanup-views` or `refactor/recipe-logic`        | `refactor(views): split recipe list and detail logic into separate files` |
| **Moving Source code(Python/Docker files)**             | `chore/move-setting`                                       | `chore(config): move settings.py into dedicated configuration folder`     |
| **Removing Source code(Python/Docker files)**           | `chore/cleanup-legacy-code` or `chore/remove-unused-utils` | `chore(utils): delete deprecated text formatting utilities`               |
| **Test Linter**                                         | `chore/manage-py-lint-test`                                | `chore(manage.py): add temporary variable to test linting`                |
| **Adding a docs**                                       | `docs/add-git-naming-standards`                            | `docs(git): add documentation for git naming standards`                   |
| **Moving Doc Files around**                             | `docs/reorganize-guides`                                   | `docs(wiki): move linux chown guide to dedicated documentation folder`    |
| **Removing Doc Files**                                  | `chore/cleanup-chomod-guid`                                | `docs(wiki): delete chmod guide`                                          |
| **updaing docs**                                        | `docs/update-naming-standards` or `docs/fix-readme-typos`  | `docs(git): update branch naming rules to include refactor and perf`      |
| **Adding a Package**                                    | `chore/add-django-stubs`                                   | `chore(deps): add django-stubs for mypy type checking`                    |
|**Adding postres dependency**|`chore/install-postgres-adapter`|`chore(deps): install psycopg2 postgres adapter`|
| **Adding a extension in devcontainer.json**             | `chore/add-prettier-extension`                             | `chore(devcontainer): add prettier extension for automated formatting`    |
| **Adding a test**                                       | `test/add-two-numbers-calculator`                          | `test(calculator): add simple test for adding two numbers`                |

### commit message

- `chore(deps): add django-stubs for mypy type checking`
- `fix(ci): silence mypy import-untyped warnings for django`
- `chore(mypy): update pyproject.toml to ignore missing imports`
- `chore(devcontainer): add prettier extension for automated formatting`
- `docs(git): add documentation for git naming standards`

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
