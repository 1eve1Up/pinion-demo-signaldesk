# Sprint excerpt

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
