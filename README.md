## Local setup on Windows: MongoDB and backend

You can run MongoDB locally either with Docker (recommended) or with the MongoDB Community installer.

### Option A: Docker Desktop

1. Install Docker Desktop for Windows.
2. Copy `.env.example` to `.env` and adjust if needed.
3. Start the stack:

```powershell
docker compose up --build -d
```

This will start services:
- backend (Django) on http://localhost:8000
- mongo on port 27017 (data persisted in a Docker volume)
- ai-service on http://localhost:8001

### Option B: Native MongoDB on Windows

1. Install MongoDB Community Server (MSI) from mongodb.com and keep defaults.
2. Ensure it runs on `mongodb://localhost:27017`.
3. Create `.env` in the project root (or use `.env.example`) and set:

```
MONGO_URI=mongodb://localhost:27017/budgetflow_db
```

4. Run the backend locally (without Docker):

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt; python manage.py migrate; python manage.py runserver 0.0.0.0:8000
```

Login/Token endpoints:
- Obtain JWT: POST http://localhost:8000/api/token/ {"username","password"}
- Refresh JWT: POST http://localhost:8000/api/token/refresh/ {"refresh"}
- Register: POST http://localhost:8000/api/auth/register {username,email?,password}
- Me: GET http://localhost:8000/api/auth/me (Authorization: Bearer <access>)

### Running tests

Tests do not require MongoDB to be running; DB calls are guarded in views used by tests.

```powershell
pytest -q
```

# BudgetFlow Backend (MVP)

Backend API for BudgetFlow. Django + DRF + MongoDB (MongoEngine), JWT auth.

## Requirements
- Python 3.12+
- MongoDB (local or Docker)
- (Optional) Docker Desktop to run Mongo/Redis via compose

## Quick start (local)
1. Create env file `.env` (already present) and ensure:
   - `MONGO_URI=mongodb://localhost:27017/budgetflow_db`
2. Install deps and run migrations:

```powershell
# from repo root
python -m venv .venv; .\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
```

3. Create a user and run the server:
```powershell
python manage.py shell -c "from django.contrib.auth import get_user_model; U=get_user_model(); u,created=U.objects.get_or_create(username='test', defaults={'email':'test@example.com'}); u.set_password('test12345'); u.save(); print('created' if created else 'updated')"
python manage.py runserver 0.0.0.0:8000
```

4. Auth and call API:
```powershell
# Get JWT
$body = '{"username":"test","password":"test12345"}'
$tok = Invoke-RestMethod -Method Post -Uri http://localhost:8000/api/token/ -ContentType 'application/json' -Body $body
$headers = @{ Authorization = "Bearer $($tok.access)" }

# Transactions
Invoke-RestMethod -Headers $headers -Uri http://localhost:8000/api/transactions/ -Method Get | ConvertTo-Json
Invoke-RestMethod -Headers $headers -Uri http://localhost:8000/api/transactions/ -Method Post -ContentType 'application/json' -Body '{"type":"income","amount":1000,"category":"Salary","description":"August"}' | ConvertTo-Json

# Goals
Invoke-RestMethod -Headers $headers -Uri http://localhost:8000/api/goals/ -Method Get | ConvertTo-Json
Invoke-RestMethod -Headers $headers -Uri http://localhost:8000/api/goals/ -Method Post -ContentType 'application/json' -Body '{"title":"MacBook","target_amount":1500,"current_amount":200,"due_date":"2025-12-31"}' | ConvertTo-Json
```

## Docker (Mongo + Redis)
If Docker Desktop is running:
```powershell
# Start services
docker compose up -d mongo redis
# Run backend in Docker (optional)
docker compose up -d backend
```

When running backend locally and services in Docker, set `MONGO_URI=mongodb://localhost:27017/budgetflow_db` in `.env`.

## API
- POST /api/transactions/
- GET  /api/transactions/
- POST /api/goals/
- GET  /api/goals/

JWT:
- POST /api/token/
- POST /api/token/refresh/

## Notes
- Django uses SQLite for auth/admin. Domain data is in MongoDB via MongoEngine.
- CORS enabled for Next.js dev origins.
- Redis is provisioned for future Celery tasks.

## CI/CD

- CI: GitHub Actions runs lint and tests on pushes and PRs. See `.github/workflows/ci.yml`.
- Docker: On pushes to `main` and tags `v*.*.*`, an image is published to GHCR at `ghcr.io/<owner>/<repo>`.

Environment variables for local dev:

- `DEBUG=1`, `ALLOWED_HOSTS=*`, `MONGO_URI=mongodb://localhost:27017/budgetflow_db`, `CORS_ALLOW_ALL_ORIGINS=true`.
- For frontend, set `NEXT_PUBLIC_API_URL=http://localhost:8000/api`.
