"""
Smoke test for the dependency upgrade (see UPGRADE_PLAN.md).

Boots the full application with a fresh database and drives the complete
user journey: register -> login -> browse all pages -> create task ->
do custom task -> change task state -> JSON endpoints.

Run from the repository root:

    venv/Scripts/python -m pytest test -q   (Windows)
    .venv/bin/python -m pytest test -q      (POSIX)
"""

import pathlib

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
DB_FILE = REPO_ROOT / "chaoswg.sqlite"


@pytest.fixture(scope="session")
def app():
    # Start from a fresh database for every test session
    for suffix in ("", "-wal", "-shm"):
        p = DB_FILE.with_name(DB_FILE.name + suffix)
        if p.exists():
            p.unlink()

    import chaoswg
    return chaoswg.app


@pytest.fixture()
def client(app):
    # The app under test is driven without a real browser CSRF token
    app.config["WTF_CSRF_ENABLED"] = False
    return app.test_client()


def register_and_login(client, app, name="alice"):
    assert client.get("/register").status_code == 200
    r = client.post("/register", data={
        "name": name,
        "password": "secret123",
        "invite_key": app.config["INVITE_KEY"],
    })
    assert r.status_code == 302, r.data
    assert r.headers["Location"] == "/login"

    r = client.post("/login", data={"name": name, "password": "secret123"})
    assert r.status_code == 302, r.data
    assert r.headers["Location"] == "/tasks"


def db_query(func):
    """Run a DB query in the test thread and close the connection afterwards.

    The app opens one connection per request (FlaskDB before_request) and
    closes it in teardown. A query executed here, outside a request, would
    leave the test-thread connection open, and peewee 3.x's connect() then
    raises "Connection already opened" on the next request (peewee 2.x used
    to silently reuse the open connection).
    """
    from chaoswg.models import db_wrapper
    try:
        return func()
    finally:
        db_wrapper.database.close()


def test_smoke(client, app):
    register_and_login(client, app)

    # All pages render (note: /admin/ is the canonical URL; Flask 308s
    # /admin there because the flask-admin index view is exposed at '/')
    for path in ["/", "/tasks", "/users", "/history",
                 "/create_task", "/do_custom_task", "/login", "/admin/"]:
        r = client.get(path)
        assert r.status_code == 200, f"GET {path} -> {r.status_code}"

    # Create a regular task
    r = client.post("/create_task", data={
        "task": "Dishes",
        "base_points": "2",
        "time_factor": "0.5",
        "schedule_days": "",
    })
    assert r.status_code == 302, r.data
    assert r.headers["Location"] == "/tasks"

    # Do a custom one-shot task
    r = client.post("/do_custom_task", data={"task": "Help a friend", "points": "3"})
    assert r.status_code == 302, r.data

    # Change task state via the AJAX endpoint
    from chaoswg.models import Task
    task = db_query(lambda: Task.get(Task.task == "Dishes"))
    r = client.post("/set_task_state", data={"id": str(task.id), "state": "2"})
    assert r.status_code == 204, r.data
    new_state = db_query(lambda: Task.get(Task.id == task.id).state)
    assert new_state == Task.DONE

    # JSON endpoints
    for path in ["/json/users", "/json/history", "/json/history/alice"]:
        r = client.get(path)
        assert r.status_code == 200, path
        assert r.is_json, path


def test_login_required(client, app):
    # Unauthenticated users are redirected to the login page
    for path in ["/tasks", "/users", "/history",
                 "/create_task", "/do_custom_task", "/admin/"]:
        r = client.get(path)
        assert r.status_code == 302, path
        assert "/login" in r.headers["Location"]
