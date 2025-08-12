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
