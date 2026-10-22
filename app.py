"""Local Docker practice app. Start with: python app.py"""
import os
import secrets
import time

import psycopg
from psycopg.rows import dict_row
from flask import Flask, abort, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
app.config.update(MAX_CONTENT_LENGTH=16384, SESSION_COOKIE_SAMESITE="Lax")


def connect_db():
    """Use keyword arguments so special characters in passwords work."""
    return psycopg.connect(
        host=os.environ.get("DB_HOST", "db"),
        port=int(os.environ.get("DB_PORT", "5432")),
        dbname=os.environ.get("DB_NAME", "tasktracker"),
        user=os.environ.get("DB_USER", "taskuser"),
        password=os.environ["DB_PASSWORD"],
        connect_timeout=3,
        row_factory=dict_row,
    )


def init_db():
    """Wait briefly for PostgreSQL and create the table without deleting data."""
    for attempt in range(1, 31):
        try:
            with connect_db() as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS tasks (
                        id BIGSERIAL PRIMARY KEY,
                        title VARCHAR(200) NOT NULL,
                        completed BOOLEAN NOT NULL DEFAULT FALSE,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
                    )
                """)
            print("Database ready; tasks table available.", flush=True)
            return
        except psycopg.OperationalError:
            if attempt == 30:
                raise RuntimeError("Database unavailable. Check DB_* settings and PostgreSQL logs.") from None
            print(f"Waiting for database ({attempt}/30)...", flush=True)
            time.sleep(2)


@app.before_request
def protect_forms():
    if request.method == "POST":
        expected = session.get("csrf_token")
        supplied = request.form.get("csrf_token", "")
        if not expected or not secrets.compare_digest(expected, supplied):
            abort(400, "Form expired. Reload the page and try again.")


@app.get("/")
def index():
    session.setdefault("csrf_token", secrets.token_hex(32))
    with connect_db() as conn:
        tasks = conn.execute("SELECT * FROM tasks ORDER BY id DESC").fetchall()
    return render_template("index.html", tasks=tasks)


@app.post("/tasks")
def add_task():
    title = request.form.get("title", "").strip()
    if not 1 <= len(title) <= 200:
        abort(400, "Enter a task containing 1 to 200 characters.")
    with connect_db() as conn:
        conn.execute("INSERT INTO tasks (title) VALUES (%s)", (title,))
    return redirect(url_for("index"), code=303)


@app.post("/tasks/<int:task_id>/toggle")
def toggle_task(task_id):
    with connect_db() as conn:
        result = conn.execute(
            "UPDATE tasks SET completed = NOT completed WHERE id = %s RETURNING id",
            (task_id,),
        ).fetchone()
        if result is None:
            abort(404)
    return redirect(url_for("index"), code=303)


@app.get("/health")
def health():
    try:
        with connect_db() as conn:
            conn.execute("SELECT 1 FROM tasks LIMIT 1")
        return {"status": "ok", "database": "connected"}
    except psycopg.Error:
        return {"status": "unavailable", "database": "unavailable"}, 503


@app.errorhandler(psycopg.Error)
def database_error(error):
    app.logger.error("Database request failed: %s", type(error).__name__)
    return "Database unavailable. Check the database container and application configuration.", 503


if __name__ == "__main__":
    if not os.environ.get("DB_PASSWORD"):
        raise SystemExit("DB_PASSWORD must be supplied as an environment variable.")
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=False)
