# Sprint 2: Core model

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

## Retrospective

### Meta

- **Date / time**: 2026-03-22
- **Scope**: sprint-2 wrap

### Stats

- **PB-1 artifact bundle:** `pinion/sprints/artifacts/sprint-2/`

- **Lines added** (sum): 1808
- **Net lines** (sum): 1722
- **Estimated input tokens** (sum): 1209

| id | lines added | net lines | est. input tok. | recorded_at |
| --- | --- | --- | --- | --- |
| PIN-018 | 391 | 369 | 145 | 2026-03-22T21:05:46Z |
| PIN-017 | 370 | 348 | 160 | 2026-03-22T21:04:51Z |
| PIN-016 | 359 | 341 | 131 | 2026-03-22T21:03:30Z |
| PIN-015 | 315 | 306 | 142 | 2026-03-22T21:02:28Z |
| PIN-014 | 144 | 135 | 166 | 2026-03-22T21:01:10Z |
| PIN-013 | 106 | 101 | 159 | 2026-03-22T21:00:09Z |
| PIN-012 | 81 | 80 | 145 | 2026-03-22T20:59:03Z |
| PIN-011 | 42 | 42 | 161 | 2026-03-22T20:57:38Z |

### What happened

All eight work units (PIN-011 through PIN-018) reached **released**. The application now matches the documented “core model”: contacts carry optional `email`, `phone`, and `company`; notes keep **`body`** as the stable content field and add optional `interaction_type` (`call`, `meeting`, `follow_up`, `other`) and timezone-aware `occurred_at`. Alembic migrations are additive and nullable, so existing rows stay valid. Pytest coverage grew (dedicated API cases plus an updated end-to-end CRM story). The repo **README** documents the new JSON shapes and PATCH behavior; **GitHub Actions** runs `pytest` on push/PR to `main` with Python 3.11, closing the Sprint 1 retro action for CI. Items in **Deferred Work** (frontend, RBAC, billing, first-class companies table, deep production hardening) were not started.

`pinion/pinion/product/product.md` was updated to align with the API, but the whole `pinion/` subtree remains **gitignored** in this demo repo, so that product copy is **local-only** unless the team changes ignore rules or force-adds files.

### 5 whys

Theme: **Why could we extend the CRM model without breaking Sprint 1 clients or tests?**

1. **Why did existing flows keep working after schema changes?** New columns and JSON fields were **optional**; defaults and migrations left prior rows and request bodies valid.
2. **Why was “optional first” feasible?** The sprint plan explicitly kept **`body`** (instead of renaming to `content`) and ordered **migrations before API** so the ORM and DB stayed in sync before clients could send new keys.
3. **Why did unknown note types not corrupt data?** Pydantic **`Literal`** validation rejects unsupported `interaction_type` values with **422**, so bad enums never reach the database.
4. **Why was that enforcement enough for this sprint?** Scope stayed a **single-owner REST slice**—no multi-tenant policy engine, no client versioning, and no need to coerce arbitrary strings to `other`.
5. **Root cause:** **Additive contracts** plus a **linear PIN chain** (schema → API → tests → docs → CI) kept each merge small, provable, and backward-compatible for the demo’s happy paths.

### Actions

- [x] Add CI that runs `pytest` on push/PR (done in PIN-018; verify green on the remote after first push).
- [ ] Decide whether `pinion/pinion/product/product.md` (or a tracked `docs/product.md`) should live **outside** the gitignored `pinion/` tree so product spec and app stay diffable in PRs.
- [ ] When opening sprint-3, set `project.active_sprint` (e.g. `pinion set-active-sprint` or edit `.pinion/config.yaml`) after planning and `pinion build`.

### Notes

**Sprint 1 carry-over:** The “add CI” action from sprint-1’s retrospective is satisfied by `.github/workflows/pytest.yml`.

**Still deferred (same themes as sprint doc):** frontend; roles beyond row ownership; billing/email/analytics; Postgres, secrets vault, rate limits, observability; `/companies` or account model; pagination and refresh tokens unless a later sprint targets them.

**Nice next PINs:** OpenAPI request/response **examples** matching README; list pagination; coerce-or-document policy if third-party clients send free-form interaction labels; Docker or deploy recipe for demos.

**Tooling:** Retro artifacts live under `pinion/pinion/sprints/artifacts/sprint-2/` (path as recorded by Pinion from the application repo root). Keep sprint markdown, metrics, and git log references consistent with that tree when reporting.
