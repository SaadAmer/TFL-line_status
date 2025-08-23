# WovenLight TfL Scheduler (FastAPI + APScheduler)

Schedules and executes queries to TfL's **Line Disruption** API and stores results.

## Tech
- FastAPI (typed, auto-docs)
- APScheduler (background scheduling)
- SQLAlchemy + SQLite
- Docker, docker-compose
- pytest

## Run

```bash
# docker-compose up --build
sudo docker compose up --build

# API at http://localhost:5555
# Interactive docs at http://localhost:5555/docs





Run tests with : python -m pytest -q tests\unit\task_tests.py

# create/use Poetry’s venv and install everything (main + dev)
poetry install --with dev

# run the API
poetry run uvicorn app.main:app --host 127.0.0.1 --port 5555 --reload

# run tests
poetry run pytest -q
# or specific files
poetry run pytest -q tests/unit/test_tasks.py
poetry run pytest -q tests/integration/test_tasks.py


i want to use poetry for package management and include the flake8 and mypy linters. These should have steps in the docker pipeline as well


scp -i "C:\Users\SaadLaptopPc\Desktop\Wovenlight\wovenlight_key.pem" -r "C:\Users\SaadLaptopPc\Desktop\Wovenlight" ubuntu@13.60.79.197:~/Wovenlight


ssh -i "C:\Users\SaadLaptopPc\Desktop\Wovenlight\wovenlight_key.pem" ubuntu@13.60.79.197

poetry run pytest -q

curl -X DELETE http://localhost:5555/tasks/1 | jq


BONUS:

FOR JWT AUTH:

enable token checking at all endpoints (router = APIRouter(dependencies=[Depends(require_auth())]))
uncomment line 18 in app/routes.py
comment out line 16 in app/routespy

set env variables to local env:

export JWT_SECRET="super-long-random-dev-secret"
export JWT_ISSUER="wovenlight-dev"
export JWT_AUD="wovenlight-api"


add env variable to docker-compose: 

JWT_SECRET=super-long-random-dev-secret
JWT_ISSUER=wovenlight-dev
JWT_AUD=wovenlight-api



Get a JWT token:
python generate_token.py

TOKEN='<paste the token here>'
curl -H "Authorization: Bearer $TOKEN" http://127.0.0.1:5555/tasks