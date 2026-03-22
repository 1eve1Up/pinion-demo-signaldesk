# Sprint 1: SignalDesk API

## Goal

Ship a minimal authenticated REST API at the repository root that persists users, contacts, and per-contact interaction notes, with pytest-backed proof of the main flows so the demo reads as a coherent SaaS-style backend.

## In-Scope Chains

1. **Foundation** — Python service layout, dependencies, health check, test harness.
2. **Data** — ORM models, migrations, and DB session wiring for User, Contact, Note.
3. **Security** — Password hashing and JWT (or equivalent bearer) issuance and verification.
4. **Auth API** — Registration and login endpoints that return usable credentials for clients.
5. **CRM surface** — Authenticated CRUD for contacts and nested notes.
6. **Quality** — Automated API tests, consistent HTTP error behavior, developer runbook.

## Deferred Work

- Frontend or mobile clients
- Roles beyond “authenticated user owns their rows”
- Billing, email, analytics, reporting
- Production deployment hardening (beyond documented local run)

## Critical Path

PIN-001 → PIN-002 → PIN-003 → PIN-004 → PIN-005 → PIN-006 → PIN-007 → PIN-008 → PIN-009 → PIN-010

Scaffold and database must exist before auth; auth before protected CRM routes; routes before broad API tests; tests before tightening errors and documentation.

## Root Targets

- **PIN-001** — Scaffold the API app, dependencies, and pytest with a simple health endpoint.

## Risks

- **Auth scope creep** — Keep to register/login + bearer validation on CRM routes; defer OAuth and refresh-token complexity unless time allows inside PIN-004–PIN-005.
- **Schema churn** — Serializing DB work (PIN-002, PIN-003) reduces merge conflicts; migrations must stay reversible enough for demo use.
- **Test flakiness** — Use isolated test DB or fixtures (PIN-008) so CI-local runs stay deterministic.

## Owner-Class Summary

All targets use **`owner_class: default`** (single allowed class in `.pinion/config.yaml`). One executor or team can walk the chain in order.

## Retrospective

### Meta

- **Date / time**: 2026-03-22
- **Scope**: sprint-1 wrap

### Stats

- **PB-1 artifact bundle:** `sprints/artifacts/sprint-1/`

- **Lines added** (sum): 0
- **Net lines** (sum): 0
- **Estimated input tokens** (sum): 1317

| id | lines added | net lines | est. input tok. | recorded_at |
| --- | --- | --- | --- | --- |
| PIN-010 | 0 | 0 | 132 | 2026-03-22T20:37:02Z |
| PIN-009 | 0 | 0 | 140 | 2026-03-22T20:34:09Z |
| PIN-008 | 0 | 0 | 133 | 2026-03-22T20:31:24Z |
| PIN-007 | 0 | 0 | 116 | 2026-03-22T20:28:31Z |
| PIN-006 | 0 | 0 | 133 | 2026-03-22T20:24:28Z |
| PIN-005 | 0 | 0 | 126 | 2026-03-22T20:21:24Z |
| PIN-004 | 0 | 0 | 124 | 2026-03-22T20:13:15Z |
| PIN-003 | 0 | 0 | 124 | 2026-03-22T20:10:14Z |
| PIN-002 | 0 | 0 | 134 | 2026-03-22T17:59:38Z |
| PIN-001 | 0 | 0 | 155 | 2026-03-22T17:55:20Z |

### What happened

All ten work units (PIN-001 through PIN-010) reached **released**. The repo root now has a working FastAPI service: SQLite + Alembic, register/login with JWT, user-scoped contacts and nested notes, broad pytest coverage (including an end-to-end CRM story), consistent JSON error envelopes, and a contributor README with `.env.example`. Sprint goal (minimal authenticated REST CRM API with pytest-backed flows) is met; items in **Deferred Work** were intentionally not started.

Merge-time **lines added / net lines** stayed at zero in Pinion stats because line stats were not captured from git in this environment (tooling limitation), not because the codebase did not change.

### 5 whys

Theme: **Why is tenant isolation trustworthy in the API we shipped?**

1. **Why do cross-user access attempts return 404 instead of leaking rows?** Because contact and note handlers resolve resources only when `owner_id` matches the authenticated user (or the note hangs off such a contact).
2. **Why is that enforced in the API layer?** Because PIN-006 and PIN-007 implemented explicit ownership queries and shared helpers before expanding test coverage.
3. **Why could we rely on that ordering?** The sprint critical path put models and migrations (PIN-002, PIN-003) before auth (PIN-004, PIN-005) and before CRM routes (PIN-006, PIN-007).
4. **Why did that ordering hold without scope creep?** The sprint doc and PIN chain kept OAuth, roles, and production hardening out of scope.
5. **Root cause:** A **thin vertical slice** with a **fixed dependency order** let security rules stay small and testable until PIN-008 and PIN-009 hardened behavior and responses.

### Actions

- [ ] Add CI (e.g. GitHub Actions) that runs `pytest` on push/PR against the app at repo root.
- [ ] Decide policy for Pinion state: either stop ignoring `pinion/` in git for shared visibility, or document that coordination artifacts are local-only for this demo.
- [ ] When planning sprint-2, run `pinion set-active-sprint <id>` after creating the sprint markdown and work units.

### Notes

**Follow-ups** (from original deferrals): no frontend; single-owner model only; no billing/email; production hardening still open (HTTPS termination, secrets management, Postgres, rate limits, observability).

**Nice later PINs:** refresh tokens or short-lived access + rotation; list pagination; structured logging; OpenAPI examples aligned with README curls; deploy recipe (Docker or platform-specific).

**Tooling:** Pinion retro wrote artifacts under `sprints/artifacts/sprint-1/` (root) and under `pinion/pinion/sprints/artifacts/sprint-1/` (nested Pinion tree); keep one narrative in this file and treat artifacts as evidence, not duplicate sources of truth for prose.
