# Synthetic execution timeline

Derived from work unit JSON in this sprint (state and latest merge record only); not a live agent log.

- **PIN-011** — state `released` — last merge `recorded_at` `2026-03-22T20:57:38Z`
  - Add Alembic migration and Contact model: nullable email, phone, and company strings with sensible max lengths and indexes only if justified by lookup behavior
- **PIN-012** — state `released` — last merge `recorded_at` `2026-03-22T20:59:03Z`
  - Add Alembic migration and Note model: optional interaction_type and optional timezone-aware occurred_at; keep body as the canonical note content column
- **PIN-013** — state `released` — last merge `recorded_at` `2026-03-22T21:00:09Z`
  - Extend contact Pydantic schemas and FastAPI routes so create, update, and read accept and return email, phone, and company with validation (email format, length caps)
- **PIN-014** — state `released` — last merge `recorded_at` `2026-03-22T21:01:10Z`
  - Extend note Pydantic schemas and FastAPI routes for interaction_type and occurred_at (optional), with documented behavior for unknown interaction_type values
- **PIN-015** — state `released` — last merge `recorded_at` `2026-03-22T21:02:28Z`
  - Expand tests/test_contacts_api.py and tests/test_notes_api.py for new fields, defaults, validation errors, and PATCH semantics
- **PIN-016** — state `released` — last merge `recorded_at` `2026-03-22T21:03:30Z`
  - Extend tests/test_crm_e2e.py so the full register-login-contacts-notes story exercises the richer model (new contact and note fields)
- **PIN-017** — state `released` — last merge `recorded_at` `2026-03-22T21:04:51Z`
  - Update repository README and pinion/pinion/product/product.md so curl examples and field names match shipped JSON (body, new contact and note fields)
- **PIN-018** — state `released` — last merge `recorded_at` `2026-03-22T21:05:46Z`
  - Add GitHub Actions workflow to run pytest on push and pull_request using Python 3.11+ and project dev dependencies from pyproject.toml
