# Task Management System

Small, correctness-focused task management product built for maintainability and safe evolution.

## Stack (Required)
- Backend: Python + Flask (API-only)
- Frontend: React
- Database: Relational database (SQLite default; PostgreSQL-ready through `DATABASE_URL`)
- ORM: SQLAlchemy (Flask-SQLAlchemy)
- Validation: Marshmallow
- Testing: pytest

## Product Scope
This product intentionally stays small and emphasizes:
- clear architecture
- business rule enforcement
- safe interfaces
- behavior-driven tests
- predictable extension points

Core capabilities:
- create/list users
- create/list/delete projects
- create/list/assign/update/delete tasks
- enforce task lifecycle and deletion constraints

## Architecture
Backend uses a strict layered structure:

```
backend/
├── app.py
├── wsgi.py
├── config.py
├── models/      # database schema only
├── services/    # business rules and transactions
├── routes/      # HTTP/controller layer only
├── schemas/     # request/response validation schemas
└── tests/       # behavior tests (pytest)
```

Layer responsibilities:
- `routes/`: request parsing, schema validation, calling services, JSON responses
- `services/`: all domain rules and orchestration logic
- `models/`: table definitions, relationships, constraints
- `schemas/`: API payload validation and shape safety

This separation is used to keep business logic out of routes and to reduce blast radius during changes.

## Data Model
- `User(id, name, email unique)`
- `Project(id, name, owner_id -> User, created_at)`
- `Task(id, title, description, status enum, project_id -> Project, assigned_to -> User nullable, created_at, updated_at)`

Key relational constraints:
- foreign keys enabled
- unique email
- non-null where required
- task status as enum (`todo`, `in_progress`, `done`)

## Enforced Business Rules
Implemented in `services/` (never trusted to frontend alone):
- task must belong to an existing project
- status must be one of `todo`, `in_progress`, `done`
- cannot move directly from `todo` to `done`
- cannot move to `in_progress` without assignment
- cannot edit title after task is `done`
- cannot delete a project if it has tasks
- cannot delete a task if status is `done`
- foreign key references validated in service layer

## API Endpoints
Users:
- `POST /users`
- `GET /users`

Projects:
- `POST /projects`
- `GET /projects`
- `DELETE /projects/<id>`

Tasks:
- `POST /tasks`
- `GET /tasks?project_id=<id>`
- `PATCH /tasks/<id>/assign`
- `PATCH /tasks/<id>/status`
- `DELETE /tasks/<id>`

Error response contract:

```json
{
  "error": "ERROR_CODE",
  "message": "Human readable explanation"
}
```

## Technical Decisions and Tradeoffs
1. Service-layer rule enforcement:
- Decision: all domain invariants live in services.
- Why: keeps HTTP/controller logic thin and testable.
- Tradeoff: more files/functions, but clearer correctness boundaries.

2. Marshmallow for request validation:
- Decision: schema-first validation at API boundary.
- Why: rejects malformed input early and consistently.
- Tradeoff: duplicate field declarations (schema + model) for clearer interfaces.

3. SQLAlchemy ORM over raw SQL:
- Decision: ORM for relational mapping and maintainable CRUD.
- Why: consistency, safer model evolution, less SQL scattering.
- Tradeoff: requires discipline to avoid implicit behavior.

4. SQLite default with PostgreSQL-ready config:
- Decision: SQLite for local simplicity; `DATABASE_URL` for PostgreSQL migration.
- Why: faster evaluator setup while preserving relational model compatibility.
- Tradeoff: SQLite behavior differs slightly from PostgreSQL in advanced cases.

5. Minimal frontend with backend-authoritative rules:
- Decision: keep UI simple and do not duplicate business rules in client.
- Why: prevents drift between client assumptions and domain truth.
- Tradeoff: user discovers some invalid transitions via backend errors rather than proactive UI restriction.

## Verification
Behavioral tests are implemented with pytest for mandatory invariants:
- invalid status transition
- lifecycle step skipping prevention
- in-progress requires assignment
- cannot delete project with tasks
- cannot modify title after done
- invalid enum rejection

Run:

```bash
cd backend
pytest -q
```

## Observability
- Backend logs validation failures and status transitions.
- Backend does not expose tracebacks to API clients.
- Frontend logs API failures and surfaces readable error messages.

## AI Usage (Transparent Summary)
AI was used as an implementation assistant, not an unquestioned source of truth.

Workflow used:
- Prompting assistance was prepared with ChatGPT and then used with Claude to accelerate scaffolded code generation for selected functionalities (API wiring, UI wiring, and baseline structure).
- Generated outputs were reviewed, corrected, and validated with tests and runtime checks.

Integrity controls applied:
- architecture rules kept strict (business logic in services only)
- required constraints and validations were explicitly enforced
- test suite used to verify mandatory rule behavior
- startup/runtime checks performed under Gunicorn

## Risks and Limitations
- No authentication/authorization yet.
- No migrations tool (e.g., Alembic) added yet; schema is created programmatically.
- Current default DB is SQLite; PostgreSQL should be used for production parity.
- Frontend is intentionally minimal and not optimized for large datasets.

## Extension Approach
To preserve change resilience:
1. Add auth as middleware + service authorization checks without moving business rules into routes.
2. Introduce roles/permissions in service methods before mutating resources.
3. Add migration tooling to safely evolve schema.
4. Expand tests by behavior contract (not implementation details).
5. Add structured request IDs/metrics for stronger observability.

## Local Run
Backend:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Development
python app.py

# Production-like
gunicorn --bind 127.0.0.1:5000 wsgi:app
```

Frontend:

```bash
cd frontend
npm install
npm run start
```

