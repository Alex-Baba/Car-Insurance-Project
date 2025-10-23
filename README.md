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

## OpenAPI & Swagger UI

The API exposes an automatically generated OpenAPI specification via `flask-smorest`.

Endpoints:

| Path | Purpose |
|------|---------|
| `/openapi.json` | Raw OpenAPI 3.0.3 document (JSON) |
| `/swagger-ui` | Interactive Swagger UI (served via CDN) |

Enabled by default (see `ENABLE_SWAGGER` in `app/core/config.py`). To disable documentation in production set:

```powershell
$env:ENABLE_SWAGGER="false"; flask run
```

Key configuration values:

| Setting | Default | Meaning |
|---------|---------|---------|
| API_TITLE | Cars Insurance API | Title displayed in Swagger UI |
| API_VERSION | v1 | API version string |
| OPENAPI_VERSION | 3.0.3 | OpenAPI spec version |
| ENABLE_SWAGGER | true | Master switch for exposing spec & UI |

Blueprint descriptions were added to enrich tag descriptions. For richer per-operation details you can:

1. Add docstrings to method handlers describing parameters & responses.
2. Use `@blp.response` and `@blp.arguments` decorators (migration from manual Pydantic validation) for automatic schema wiring.
3. Register reusable components (e.g. error schema) and reference with `$ref` in responses.

Example (future enhancement) converting a POST to decorator style:

```python
@policies_bp.route('/policies')
class InsurancePolicyCollection(MethodView):
  @policies_bp.response(201, PolicyOut)  # success
  @policies_bp.arguments(PolicyCreate)   # request body
  def post(self, body):
    p = create_policy(body.provider, body.startDate, body.endDate, body.carId)
    return PolicyOut.model_validate(p, from_attributes=True)
```

Exporting spec to a file (optional for CI artifact):

```powershell
curl http://localhost:8000/openapi.json -o openapi.json
```

You can bundle it with ReDoc locally:

```powershell
npx redoc-cli build openapi.json -o docs.html
```

Planned enhancements:
- Add operation examples (request/response bodies)
- Standardize error responses to RFC 7807 (problem+json) component
- Add pagination query parameters & schemas (`limit`, `offset`, `meta`)
- Security scheme components once auth is introduced

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

## Postman Showcase

Use the following curated examples to demonstrate both successful operations and error handling. Base URL: `http://localhost:8000`.

### Execution Order
1. Create Owner
2. Create Car (using ownerId)
3. Create Policy
4. Create Overlapping Policy (error 409)
5. Create Claim
6. Query History
7. Insurance Validity (insured + uninsured date)
8. Error cases (bad dates, missing fields, 404, validation)

### Owners
Create Owner (201):
```http
POST /api/owners
Content-Type: application/json

{
  "name": "Alice Driver",
  "email": "alice@example.com"
}
```
Response (excerpt):
```json
{
  "id": 1,
  "name": "Alice Driver",
  "email": "alice@example.com"
}
```
Missing Name (422/400):
```http
POST /api/owners
{
  "email": "missing@example.com"
}
```
Expected: validation error payload.

### Cars
Create Car (201):
```http
POST /api/cars
{
  "vin": "VINPOSTMAN0001",
  "make": "Ford",
  "model": "Focus",
  "yearOfManufacture": 2020,
  "ownerId": 1
}
```
Get Non-existent Car (404):
```http
GET /api/cars/999999
```

### Policies
Create Policy (201):
```http
POST /api/policies
{
  "carId": 1,
  "provider": "ACME",
  "startDate": "2025-01-01",
  "endDate": "2025-06-30"
}
```
Overlap Conflict (409):
```http
POST /api/policies
{
  "carId": 1,
  "provider": "OverlapCo",
  "startDate": "2025-06-01",
  "endDate": "2025-08-01"
}
```
Bad Dates (endDate < startDate) (400/422):
```http
POST /api/policies
{
  "carId": 1,
  "provider": "BadDates",
  "startDate": "2025-02-10",
  "endDate": "2025-02-01"
}
```
Non-existent Car (404):
```http
POST /api/policies
{
  "carId": 999999,
  "provider": "Ghost",
  "startDate": "2025-01-01",
  "endDate": "2025-02-01"
}
```

### Claims
Create Claim (201):
```http
POST /api/claims/car/1
{
  "description": "Rear bumper dent",
  "claimDate": "2025-03-10",
  "amount": 350.00
}
```
Negative Amount (400/422):
```http
POST /api/claims/car/1
{
  "description": "Invalid amount test",
  "claimDate": "2025-03-11",
  "amount": -10
}
```
Non-existent Car (404):
```http
POST /api/claims/car/999999
{
  "description": "Ghost car",
  "claimDate": "2025-03-12",
  "amount": 100
}
```

### History
Get History (200):
```http
GET /api/history/1
```
Non-existent Car History (404):
```http
GET /api/history/999999
```

### Insurance Validity
Insured Date (200):
```http
GET /api/cars/1/insurance-valid?date=2025-05-05
```
Uninsured Date (200):
```http
GET /api/cars/1/insurance-valid?date=2026-01-01
```
Missing Date Param (400):
```http
GET /api/cars/1/insurance-valid
```

### Deletions
Delete Policy (204):
```http
DELETE /api/policies/<policy_id>
```
Delete Claim (204):
```http
DELETE /api/claims/<claim_id>
```
Cascade Delete Car (204):
```http
DELETE /api/cars/1
```
Repeat Delete (404):
```http
DELETE /api/cars/1
```

### Typical Error Payloads
Conflict (409):
```json
{
  "status": 409,
  "title": "Conflict",
  "detail": "Policy dates overlap existing policy"
}
```
Validation (422 example):
```json
{
  "status": 422,
  "title": "Validation Error",
  "errors": [
    { "loc": ["endDate"], "msg": "endDate must be >= startDate", "type": "value_error" }
  ]
}
```
Not Found (404):
```json
{
  "status": 404,
  "title": "Not Found",
  "detail": "Car not found"
}
```

### Postman Collection Import (Raw JSON Skeleton)
Import via Postman > Import > Raw Text:
```json
{
  "info": {
    "name": "Cars Insurance API Showcase",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Owner - Create",
      "request": {
        "method": "POST",
        "header": [{"key":"Content-Type","value":"application/json"}],
        "url": {"raw": "{{baseUrl}}/api/owners", "host": ["{{baseUrl}}"], "path": ["api","owners"]},
        "body": {"mode":"raw","raw":"{\n  \"name\": \"Alice Driver\",\n  \"email\": \"alice@example.com\"\n}"}
      }
    },
    {
      "name": "Car - Create",
      "request": {
        "method": "POST",
        "header": [{"key":"Content-Type","value":"application/json"}],
        "url": {"raw": "{{baseUrl}}/api/cars", "host": ["{{baseUrl}}"], "path": ["api","cars"]},
        "body": {"mode":"raw","raw":"{\n  \"vin\": \"VINPOSTMAN0001\",\n  \"make\": \"Ford\",\n  \"model\": \"Focus\",\n  \"yearOfManufacture\": 2020,\n  \"ownerId\": {{ownerId}}\n}"}
      }
    },
    {
      "name": "Policy - Create",
      "request": {
        "method": "POST",
        "header": [{"key":"Content-Type","value":"application/json"}],
        "url": {"raw": "{{baseUrl}}/api/policies", "host": ["{{baseUrl}}"], "path": ["api","policies"]},
        "body": {"mode":"raw","raw":"{\n  \"carId\": {{carId}},\n  \"provider\": \"ACME\",\n  \"startDate\": \"2025-01-01\",\n  \"endDate\": \"2025-06-30\"\n}"}
      }
    },
    {
      "name": "Policy - Overlap Conflict",
      "request": {
        "method": "POST",
        "header": [{"key":"Content-Type","value":"application/json"}],
        "url": {"raw": "{{baseUrl}}/api/policies", "host": ["{{baseUrl}}"], "path": ["api","policies"]},
        "body": {"mode":"raw","raw":"{\n  \"carId\": {{carId}},\n  \"provider\": \"OverlapCo\",\n  \"startDate\": \"2025-06-01\",\n  \"endDate\": \"2025-08-01\"\n}"}
      }
    },
    {
      "name": "Claim - Create",
      "request": {
        "method": "POST",
        "header": [{"key":"Content-Type","value":"application/json"}],
        "url": {"raw": "{{baseUrl}}/api/claims/car/{{carId}}", "host": ["{{baseUrl}}"], "path": ["api","claims","car","{{carId}}"]},
        "body": {"mode":"raw","raw":"{\n  \"description\": \"Rear bumper dent\",\n  \"claimDate\": \"2025-03-10\",\n  \"amount\": 350.00\n}"}
      }
    },
    {
      "name": "Validity - Insured",
      "request": {"method":"GET","url": {"raw": "{{baseUrl}}/api/cars/{{carId}}/insurance-valid?date=2025-05-05", "host": ["{{baseUrl}}"], "path": ["api","cars","{{carId}}","insurance-valid"], "query": [{"key":"date","value":"2025-05-05"}]}}
    },
    {
      "name": "Validity - Missing Date (Error)",
      "request": {"method":"GET","url": {"raw": "{{baseUrl}}/api/cars/{{carId}}/insurance-valid", "host": ["{{baseUrl}}"], "path": ["api","cars","{{carId}}","insurance-valid"]}}
    }
  ],
  "variable": [
    {"key":"baseUrl","value":"http://localhost:8000"},
    {"key":"ownerId","value":"1"},
    {"key":"carId","value":"1"}
  ]
}
```

Adjust variables after creating resources, then replay dependent requests.