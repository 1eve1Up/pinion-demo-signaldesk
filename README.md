# SignalDesk API

Minimal authenticated REST API: users, contacts, and per-contact notes (SQLite by default). Requires **Python 3.11+** (see `requires-python` in `pyproject.toml`).

## Setup

From the repository root (the directory that contains `pyproject.toml`):

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

## Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `JWT_SECRET_KEY` | **Yes** | Secret for signing access tokens (HS256). Must be set for register, login, and protected routes. |
| `DATABASE_URL` | No | Async SQLAlchemy URL. Default: `sqlite+aiosqlite:///./signaldesk.db` (file created next to the process working directory). |

Optional: `JWT_ALGORITHM` (default `HS256`), `ACCESS_TOKEN_EXPIRE_MINUTES` (default `30`).

Copy the template, edit the secret, and run commands from the repo root so the app can read `.env`:

```bash
cp .env.example .env
# edit .env — JWT_SECRET_KEY must be non-empty
```

Variables can still be set only in the shell environment if you prefer; they override values from `.env`.

## Database migrations

With the venv active and env vars set (at least `JWT_SECRET_KEY` for a full run):

```bash
cd /path/to/pinion-demo-signaldesk
alembic upgrade head
```

## Run the API server

```bash
uvicorn signaldesk.main:app --reload --host 127.0.0.1 --port 8000
```

- OpenAPI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Health: `GET /health` returns `{"status":"ok"}`.

## Run tests

```bash
pytest
```

Tests use an isolated temporary database and set `JWT_SECRET_KEY` themselves; you do not need a running server.

## Example `curl` flows

Replace `BASE` if you use another host or port. Error responses use JSON like `{"error":"<code>","message":"<text>"}` (and `details` for validation errors).

### Register and use the returned token

```bash
BASE=http://127.0.0.1:8000

curl -sS -X POST "$BASE/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@example.com","password":"your-secure-password"}'
```

Copy `access_token` from the JSON response, then:

```bash
TOKEN='<paste access_token here>'

curl -sS "$BASE/contacts" -H "Authorization: Bearer $TOKEN"
```

### Log in (same JSON fields as register: `email`, `password`)

```bash
curl -sS -X POST "$BASE/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@example.com","password":"your-secure-password"}'
```

### CRM-style calls (contacts and notes)

```bash
# Create a contact (`name` is required)
curl -sS -X POST "$BASE/contacts" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Acme Corp"}'

# Replace CONTACT_ID with the id from the response
CONTACT_ID=1

curl -sS "$BASE/contacts/$CONTACT_ID" -H "Authorization: Bearer $TOKEN"

# Add a note (`body` is required)
curl -sS -X POST "$BASE/contacts/$CONTACT_ID/notes" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"body":"Called - follow up next week."}'

curl -sS "$BASE/contacts/$CONTACT_ID/notes" -H "Authorization: Bearer $TOKEN"
```

## Pinion (optional)

This repo can carry a `pinion/` subtree for task tracking. See `pinion/AGENTS.md` and run `./bin/pinion` from inside `pinion/` for CLI help.
