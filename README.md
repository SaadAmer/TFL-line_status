# WovenLight TfL Scheduler Service

This project is a Python web service that schedules calls to Transport for London’s (TfL) Line API to retrieve line disruption information.  
It demonstrates REST API design, background scheduling, database persistence, logging, and containerization.

---

## Features

- **Task Scheduling**
  - Add tasks specifying tube line IDs and a schedule time.
  - If no schedule time is provided, the task runs immediately.
- **Task Management**
  - Get all tasks or by ID (with status & results).
  - Update task lines or schedule time (if still scheduled).
  - Delete tasks.
- **TfL Line Disruptions**
  - Fetches disruptions from [`https://api.tfl.gov.uk/Line/*`](https://api.tfl.gov.uk/).
- **Database**
  - Defaults to SQLite (local env/dev/tests).
  - Supports PostgreSQL via `DATABASE_URL` on docker.
- **Scheduler**
  - Uses APScheduler for background jobs.
- **Logging**
  - Structured JSON logs with request/response context.
- **Authentication (BONUS)**
  - Optional JWT protection for all endpoints.

---

## Endpoints

### Create Task
```bash
curl -X POST -H 'Content-Type: application/json' -d '{"scheduler_time" : "2021-11-12T17:00:00", "lines":"victoria"}' http://localhost:5555/tasks
```

### Create Task with Alias scheduler_time

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"scheduler_time": "2026-11-12T17:00:00", "lines":"victoria,central"}' \
  http://127.0.0.1:5555/tasks
```

### List Tasks

```bash
curl http://127.0.0.1:5555/tasks
```

### Get Task by ID

```bash
curl http://127.0.0.1:5555/tasks/<id>
```

### Update Task

```bash
curl -X PATCH -H "Content-Type: application/json" \
  -d '{"lines": "victoria,central"}' \
  http://127.0.0.1:5555/tasks/<id>
```

### Delete Task

```bash
curl -X DELETE http://127.0.0.1:5555/tasks/<id>
```


## Local Development

### Install dependencies


```bash
poetry install
```

### Run with SQLite (default)

```bash
poetry run uvicorn app.main:app --reload --host 127.0.0.1 --port 5555
```

### Run Tests

```bash
pytest -q
```

### Running with Docker

```bash
docker compose up --build
```

You can find the docs at http://localhost:5555/docs


## Bonus Optional JWT Auth
### To Enable JWT AUTH:

Enable token checking at all endpoints (router = APIRouter(dependencies=[Depends(require_auth())]))
Uncomment line 18 in app/routes.py
Comment out line 16 in app/routespy

Set env variables to local env:

```bash
export JWT_SECRET="super-long-random-dev-secret"
export JWT_ISSUER="wovenlight-dev"
export JWT_AUD="wovenlight-api"
```

Add env variable to docker-compose: 

```bash
JWT_SECRET=super-long-random-dev-secret
JWT_ISSUER=wovenlight-dev
JWT_AUD=wovenlight-api
```


### Get a JWT token:

Run the following command

```bash
python generate_token.py
```

Paste the token here:

```bash
TOKEN='<paste the token here>'
```

Use as Follows:

```bash
curl -H "Authorization: Bearer $TOKEN" http://127.0.0.1:5555/tasks
```