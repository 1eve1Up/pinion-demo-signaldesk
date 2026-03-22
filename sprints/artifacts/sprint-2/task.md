# Sprint excerpt

## Goal

Align the SignalDesk CRM database model, REST API, automated tests, and written product docs with the documented core model (contacts with email, phone, and company; notes with interaction type and occurred-at semantics), and add GitHub Actions that run `pytest` on push and PR—without opening Sprint 1 deferrals (frontend, RBAC, billing, deep production hardening).

## In-Scope Chains

1. **Schema — contacts** — Alembic revision(s) adding nullable `email`, `phone`, and `company` on `contacts` with sensible lengths; update the SQLAlchemy model.
2. **Schema — notes** — Alembic revision(s) adding optional `interaction_type` and optional timezone-aware `occurred_at` on `notes`; keep JSON field `body` as the stable content field (align product copy to `body`).
3. **API — contacts** — Extend Pydantic schemas and FastAPI handlers for create, update, and read paths including the new contact fields with validation (e.g. email format, length caps).
4. **API — notes** — Extend Pydantic schemas and FastAPI handlers for the new note fields, including sensible handling of unknown `interaction_type` values (per implementation choice in the target).
5. **Tests — APIs** — Expand contact and note API tests for new fields, defaults, and PATCH semantics.
6. **Tests — E2E** — Extend the full CRM pytest story to exercise the richer model end-to-end.
7. **Docs** — Update repository README and `pinion/pinion/product/product.md` so examples and field names match shipped JSON.
8. **CI** — Add a workflow under `.github/workflows/` running `pytest` with Python 3.11+ on push/PR.

## Deferred Work

- Frontend or mobile clients
- Roles beyond single-owner row scoping
- Billing, email, analytics, reporting
- Production deployment hardening (HTTPS, secrets vault, Postgres, rate limits, structured logging, deploy recipes)—except the narrow CI addition above
- First-class `Company` / `Account` table and `/companies` CRUD (optional stretch deferred to a later sprint)
- Pagination, refresh tokens, and other platform niceties called out in Sprint 1 retrospective as non-goals for this sprint

## Critical Path

PIN-011 → PIN-012 → PIN-013 → PIN-014 → PIN-015 → PIN-016 → PIN-017 → PIN-018

Migrations and models land before API and schema changes; API before focused tests; tests before doc alignment; docs before CI so the workflow reflects accurate instructions.

## Root Targets

- **PIN-011** — Add Alembic migration and Contact model fields: nullable `email`, `phone`, and `company`.

## Risks

- **Breaking API** — Renaming `body` to `content` would break clients; this sprint keeps `body` and updates product text to match.
- **Migration defaults** — New columns stay nullable so existing rows need no backfill.
- **Enum drift** — Clients may send unknown `interaction_type` values; implementation should reject clearly or coerce to a documented fallback (e.g. `other`).
- **CI environment** — Workflow must install the same dependency extras and use the same Python baseline as local `pytest`.

## Owner-Class Summary

All targets use **`owner_class: default`** (the only allowed class in `.pinion/config.yaml`). One executor or team can walk the chain in order.
