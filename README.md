# Task Tracker — Docker practice assignment


# My Docker Task Tracker

A Flask task-tracking application backed by PostgreSQL 16.

## Requirements

- Docker Engine
- Docker Compose plugin

## Configuration

Create a `.env` file containing:

```dotenv
POSTGRES_DB=tasktracker
POSTGRES_USER=taskuser
POSTGRES_PASSWORD=replace_with_your_password
DB_HOST=db
DB_PORT=5432
DB_NAME=tasktracker
DB_USER=taskuser
DB_PASSWORD=replace_with_your_password
```

Use the same password for both password settings.

## Start

```bash
docker compose up -d
```

Open http://localhost:8080 on the machine running Docker.
For my Vagrant lab, access it from Windows at:
http://192.168.56.10:8080

## Check status

```bash
docker compose ps
curl http://localhost:8080/health
```

## Stop and remove containers

```bash
docker compose down
```

The named database volume remains, preserving tasks.

## Published image

anex4real/task-tracker:v3





You are the DevOps engineer. The developer has supplied a working application;
your task is to package it and connect it to PostgreSQL. Dockerfile,
compose.yaml and .dockerignore are deliberately not supplied.

## Start here

1. Extract this project into a NEW folder called task-tracker. Keep your
   existing Flask/Redis compose-demo separate.
2. Read the application contract below.
3. Write your Dockerfile first and send it for review.
4. Then tackle networking, PostgreSQL, persistence and Compose.

## Application contract (information a developer would give you)

- Runtime: Python 3.12. Dependencies are in requirements.txt.
- Start command: `python app.py` (use this command, not `flask run`, because
  it performs the startup database initialization).
- Listening address: 0.0.0.0, port 5000 inside the application container.
- Required files: app.py, requirements.txt, templates/ and static/.
- PostgreSQL baseline for this exercise: major version 16. The database and
  login role must exist before the application connects; the role needs
  permission to create tables in that database.
- The application creates its tasks table automatically and retries database
  connectivity up to 30 times, with 2-second pauses and 3-second connection
  timeouts. It does not delete existing tasks on startup.
- GET / displays the UI. POST /tasks adds a task. POST /tasks/<id>/toggle
  completes or reopens it. GET /health checks database/table availability:
  200 when ready, 503 when unavailable.

## Configuration expected by the application

| Variable | Default | Meaning |
|---|---|---|
| DB_HOST | db | Database hostname or Compose service name |
| DB_PORT | 5432 | Database listening port |
| DB_NAME | tasktracker | Existing PostgreSQL database |
| DB_USER | taskuser | PostgreSQL login role |
| DB_PASSWORD | Required | Password for that role |
| SECRET_KEY | Random at startup | Optional persistent Flask session signing key |

`.env.example` documents sample settings. The app reads environment variables;
it DOES NOT read a .env file automatically. Creating a .env file alone does
not put variables into a container: configure that explicitly yourself.
The official PostgreSQL image has its own initialization variable names
(POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD). Match their VALUES to the
application's DB_NAME, DB_USER and DB_PASSWORD.

## Your requirements

1. Build an image for the application and exclude local secrets/cache files
   from its build context.
2. Run PostgreSQL in a separate container using its official image.
3. Connect the services using a Docker network and database service name.
4. Publish the application on port 8080 of your Ubuntu VM.
5. Keep tasks in a named database volume across container recreation.
6. Supply credentials at runtime; keep them out of images and Git.
7. Write a Compose file to reproduce the whole setup.
8. Extend this README with your setup commands, screenshot and lessons learned.

Use the official PostgreSQL 16 image documentation to find its persistence
directory. Do not assume every PostgreSQL major version uses the same layout.
Changing initialization credentials after populating a database volume does
not automatically change the existing database role's password.

## Acceptance checks

- Visit http://192.168.56.10:8080 from Windows Chrome (your VM's private IP).
  Windows localhost requires a separate Vagrant forwarding rule.
- Add three tasks and complete one. Refresh: the state should be unchanged.
- Remove and recreate the application and database containers while keeping
  the named volume. All three tasks and their completion state must remain.
- Stop the database: /health should return 503. Restart it: /health should
  recover to 200 without rebuilding the application.
- A blank task is rejected; a title containing an apostrophe works.
- Do not remove the named volume when testing persistence.

This is a single-user local learning app with Flask's development server,
debugging disabled and basic form CSRF protection. It has no login system;
keep it in your local lab. Use one application instance for this exercise.
With the default random SECRET_KEY, refresh the page after an app restart
before submitting a form.

## References (consult when needed; no completed Docker solution included)

- Flask: https://flask.palletsprojects.com/en/stable/quickstart/
- Psycopg: https://www.psycopg.org/psycopg3/docs/basic/usage.html
- PostgreSQL image: https://hub.docker.com/_/postgres

Dependency versions are bounded ranges, not a fully pinned lockfile.

## Validation of this starter

Python syntax and Flask route/form checks passed with a mocked database,
including HTML escaping, CSRF checks, title validation and health responses.
A live PostgreSQL/container integration test was not run in the preparation
environment; complete the acceptance checks in your Docker lab.
