<div align="center">
  <h1>Cars Insurance API</h1>
  <p>Domain-driven Flask + SQLAlchemy service for car ownership, policies, claims, validity checks & history.</p>
  <p><strong>Status:</strong> Active Development</p>
</div>

## Overview

The Cars Insurance API manages car owners, vehicles, insurance policies and claims. It enforces key domain rules:

- Policies for a car must not overlap in time.
- Policy dates must follow chronological order (start_date < end_date).
- Claims associate to a car and appear in unified chronological history alongside policies.
- Daily expiry logging job (optional) records policies ending today.
- Insurance validity endpoint checks if a car is insured on a given date.

Stack Highlights:

- Flask 3 + flask-smorest (Blueprints / OpenAPI scaffolding)
- SQLAlchemy 2.x ORM + Alembic migrations
- Pydantic v2 for request/response schema validation & serialization
- structlog for structured logging (request ID & policy expiry events)
- APScheduler for scheduled expiry logging (optional)
- Gunicorn for production WSGI serving
- Docker / docker-compose for containerized deployment (Postgres)

## Project Structure

```
app/
  main.py               # Flask app factory & startup
  api/
    routers/            # Blueprints/endpoints
      cars.py
      claims.py
      policies.py
      history.py
      health.py
      owner.py
      insuranceValidation.py
    errors.py           # exception handler registrations & error types
    schemas.py          # Pydantic v2 request/response models
  core/
    config.py           # pydantic-settings (env driven)
    logging.py          # structlog setup
    scheduling.py       # APScheduler init & jobs
    request_id.py       # request ID middleware
  db/
    base.py             # SQLAlchemy db init (Flask SQLAlchemy wrapper)
    models.py           # ORM models
  services/             # Business logic layer
    car_service.py
    claim_service.py
    expiry_service.py
    history_service.py
    owners_service.py
    policies_service.py
    validity_service.py
  utils/
    date.py             # date helpers
migrations/             # Alembic migration scripts
tests/                  # Pytest suite
```

## Features

- Owners CRUD (create owners, list owners)
- Cars CRUD with owner linkage
- Policies CRUD with overlap prevention & date validation
- Claims creation & listing
- Unified history endpoint (policies + claims ordered chronologically)
- Insurance validity checker for arbitrary date queries
- Daily policy expiry logging job (scheduler) with idempotency safeguard
- Centralized domain error handling for clean JSON error responses

## Running Locally (Python)

Install dependencies and run tests:

```powershell
pip install -r requirements.txt
pytest -q
```

Run the dev server (SQLite by default):

```powershell
python -c "from app.main import create_app; app=create_app(); app.run(debug=True)"
```

## Configuration

Settings resolved via `pydantic-settings` (`app/core/config.py`). Environment variables override defaults; a `.env` file may be used locally.

Important variables:

| Variable | Purpose | Default |
|----------|---------|---------|
| APP_ENV | Environment name | dev |
| DATABASE_URL | SQLAlchemy connection string | sqlite:///data.db |
| LOG_LEVEL | Root log level | INFO |
| LOG_TO_FILE | Enable rotating file log (not in docker by default) | 1 (local) |
| SCHEDULER_ENABLED | Enable APScheduler job | False |
| EXPIRY_JOB_INTERVAL_MINUTES | Interval for expiry logging (dev) | 10 |

## Docker

Build and start the stack (Flask API + Postgres):

```powershell
docker compose build
docker compose up -d
```

The API will be available at http://localhost:8000. Swagger UI (if enabled) at http://localhost:8000/swagger-ui.

Environment variables (compose overrides):

- APP_ENV=docker
- DATABASE_URL=postgresql+psycopg2://insurance:insurance@db:5432/insurance
- LOG_LEVEL=INFO
- SCHEDULER_ENABLED=false

To run migrations manually inside the container:

```powershell
docker compose exec app alembic upgrade head
```

View logs:

```powershell
docker compose logs -f app
```

Stop and remove:

```powershell
docker compose down -v
```

### Healthcheck (Optional Compose Addition)

You can add a healthcheck to `app` service:

```yaml
  app:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 15s
```

## Running Tests in Docker

Execute tests inside the built image (ephemeral container):

```powershell
docker compose run --rm app pytest -q
```

## Endpoints (Summary)

Below are the primary RESTful resource endpoints. New nested & item endpoints were added; legacy flat collection endpoints remain (for backward compatibility and existing tests) but will be deprecated.

| Method | Path | Status Codes | Description |
|--------|------|-------------|-------------|
| GET | /api/health | 200 | Basic health info |
| GET | /api/owners | 200 | List owners |
| POST | /api/owners | 201 + Location | Create owner |
| GET | /api/owners/<owner_id> (planned) | 200 / 404 | Retrieve single owner (pending implementation) |
| GET | /api/cars | 200 | List cars |
| POST | /api/cars | 201 + Location | Create car |
| GET | /api/cars/<car_id> | 200 / 404 | Retrieve single car |
| DELETE | /api/cars/<car_id> | 204 / 404 | Delete car (cascade policies & claims) |
| GET | /api/cars/<car_id>/policies | 200 | List policies for a car (preferred) |
| POST | /api/cars/<car_id>/policies | 201 + Location / 409 | Create policy for car (overlap validation) |
| GET | /api/policies (legacy) | 200 | List all policies (will be deprecated) |
| GET | /api/policies/<policy_id> | 200 / 404 | Retrieve policy |
| PUT | /api/policies/<policy_id> | 200 / 404 / 409 | Update policy (overlap validation) |
| DELETE | /api/policies/<policy_id> | 204 / 404 | Delete policy (removes only that policy) |
| GET | /api/claims (legacy) | 200 | List all claims (will be deprecated) |
| GET | /api/claims/car/<car_id> | 200 | List claims for a car (preferred) |
| POST | /api/claims/car/<car_id> | 201 + Location / 404 | Create claim for a car |
| GET | /api/claims/<claim_id> | 200 / 404 | Retrieve claim |
| DELETE | /api/claims/<claim_id> | 204 / 404 | Delete claim (irreversible) |
| GET | /api/history/<car_id> | 200 / 404 | Chronological history (policies + claims) |
| GET | /api/cars/<car_id>/history (planned) | 200 / 404 | Nested history endpoint (will replace /api/history/<car_id>) |
| GET | /api/cars/<car_id>/insurance-valid | 200 / 404 | Insurance validity for a car/date |

Notes:
1. 201 responses include a Location header pointing to the newly created resource (e.g. /api/policies/<id>). Cars & owners will gain Location headers shortly.
2. 204 DELETE responses return no body.
3. Overlap conflicts for policies return 409 with a structured error payload.
4. Legacy endpoints will emit deprecation warnings in a future release before removal.
5. DELETE endpoints for policies and claims are implemented as shown; ensure you target the item resource path with the numeric ID.

### REST Conventions

- Nouns & hierarchy: Child resources (policies, claims, history) are nested under their parent car where context is required.
- Consistent status codes: 200 (success fetch/update), 201 (created), 204 (deleted), 400 (validation), 404 (not found), 409 (conflict), 500 (unexpected).
- Location header: Returned on successful creation for addressable resources.
- Idempotent deletes: Repeated DELETE of a missing resource yields 404 (no silent success masking).
- Validation first: Domain rules (date ordering, overlap) raise ConflictError or DomainValidationError early.

## Response Models

All responses use Pydantic v2 models in `app/api/schemas.py`. They are serialized with `by_alias=True` for camelCase consistency (e.g. `startDate`, `endDate`, `claimDate`).

## Error Handling

Custom domain errors produce consistent JSON:

```json
{
  "error": "DomainValidationError",
  "message": "Policy dates overlap existing policy",
  "field": "dateRange"
}
```

Other exceptions are transformed into structured responses (see `app/api/errors.py`). ConflictError returns 409. A full RFC 7807-style envelope (problem+json) will be rolled out incrementally:

```json
{
  "type": "https://example.com/problem/policy-overlap",
  "title": "Conflict",
  "status": 409,
  "detail": "Policy dates overlap existing policy",
  "instance": "/api/policies/123"
}
```

Current responses use a simpler error shape; migration to the above format is planned (see Roadmap).

## Image Details

Multi-stage build (builder wheels + slim runtime). Gunicorn serves the Flask app via the factory `app.main:create_app()`. Entry script runs Alembic migrations first.

## Scheduler (Policy Expiry Logging)

When enabled (`SCHEDULER_ENABLED=true`) the expiry job marks policies ending today in a guarded midnight window and logs them with `policy.expiry` event.

## Customizing

Override the database:

```powershell
docker compose run --rm -e DATABASE_URL=sqlite:///data.db app alembic upgrade head
```

Enable scheduler (expiry logging job):

```powershell
docker compose run --rm -e SCHEDULER_ENABLED=true app
```

## Health

Health endpoint: `GET /api/health` returns basic status.

## Development Tips

- Use SQLite for quick local prototyping: `DATABASE_URL=sqlite:///dev.db`.
- Run `alembic revision --autogenerate -m "description"` after model changes.
- Keep migrations linear (avoid editing old migrations in production). For idempotent fixes, create a new revision.
- Use structured logging for debugging complex flows: `log.info("policy.create", policy_id=...)`.

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| Duplicate index error on migration | Edited old migration clashing with baseline | Drop DB volume or create corrective migration |
| PermissionError writing app.log in Docker | Non-root user lacks write path | Disable file logging or create writable `logs/` directory before USER |
| Overlap policy rejection | New policy date range intersects existing | Adjust start/end dates to non-overlapping window |
| History dates ordering odd | Datetime serialization format mismatch | Ensure ISO strings & consistent `HistoryEntryOut` model |

## Roadmap

- Pagination & filtering for list endpoints
- Authentication & authorization layer
- OpenAPI schema enhancements (examples, descriptions)
- Background jobs for stale policy cleanup
- Observability: metrics (Prometheus) & tracing
- Session utility helpers (`session.py`) for transactional operations

## License

Currently unlicensed (private/internal). Add a LICENSE file before public distribution.

## Contributing

1. Fork & branch: `feat/your-feature`
2. Add/adjust tests
3. Run `pytest -q` locally
4. Open PR with summary of change & screenshots/logs if relevant

## Security

No auth layer yet; do not expose publicly without adding authentication & rate limiting.

- For production consider adding a non-root DB migration step in CI/CD.
- Adjust Gunicorn workers/threads based on CPU and workload.
- Add a separate Dockerfile.dev for faster iterative development (editable volume, no wheel build) if needed.