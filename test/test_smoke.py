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
import re

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
    leave the test-thread connection open, and peewee's connect() then
    raises "Connection already opened" on the next request (verified with
    peewee 4.4.0; the old app relied on the pre-3.x silent reuse).
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


def test_history_of_user_without_tasks(client, app):
    """A user who has done no tasks yet must not break their history page.

    /json/history/<username> then returns [] and history_user.js used to
    crash on result[0].time ("Cannot read properties of undefined
    (reading 'time')"). Both the JSON payload and the rendered empty state
    are checked here."""
    register_and_login(client, app, name="carol")

    r = client.get("/json/history/carol")
    assert r.status_code == 200
    assert r.get_json() == []

    r = client.get("/history/carol")
    assert r.status_code == 200
    assert "No tasks completed yet." in r.get_data(as_text=True)


def test_login_required(client, app):
    # Unauthenticated users are redirected to the login page
    for path in ["/tasks", "/users", "/history",
                 "/create_task", "/do_custom_task", "/admin/"]:
        r = client.get(path)
        assert r.status_code == 302, path
        assert "/login" in r.headers["Location"]


def _admin_csrf_token(client, path):
    """Admin forms are flask-admin SecureForms (WTForms SessionCSRF), not
    flask-wtf FlaskForms, so WTF_CSRF_ENABLED does not apply. A real browser
    submits the hidden token; do the same here."""
    r = client.get(path)
    assert r.status_code == 200, path
    m = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', r.get_data(as_text=True))
    assert m, f"no csrf token in {path}"
    return m.group(1)


def test_admin(client, app):
    """flask-admin 2.x: the CRUD interface must keep working."""
    register_and_login(client, app, name="bob")

    from chaoswg.models import Task
    task_id = db_query(lambda: Task.get(Task.task == "Dishes").id)

    # Admin pages render for an authenticated user. Note: flask-admin 2.x
    # moved the object id out of the path into a query parameter.
    for path in ["/admin/", "/admin/task/", "/admin/user/", "/admin/history/",
                 "/admin/task/new/", f"/admin/task/edit/?id={task_id}"]:
        r = client.get(path)
        assert r.status_code == 200, (path, r.status_code)

    # Create a task through the admin interface
    token = _admin_csrf_token(client, "/admin/task/new/")
    r = client.post("/admin/task/new/", data={
        "csrf_token": token,
        "task": "Admin-created",
        "base_points": "5",
        "time_factor": "0",
        "state": "0",
        "todo_time": "",
        "last_done": "",
        "schedule_days": "",
    })
    assert r.status_code == 302, r.data
    assert "/admin/task/" in r.headers["Location"]
    new_id = db_query(lambda: Task.get(Task.task == "Admin-created").id)
    assert db_query(lambda: Task.get(Task.id == new_id).base_points) == 5

    # Edit it to TODO through the admin interface
    token = _admin_csrf_token(client, f"/admin/task/edit/?id={new_id}")
    r = client.post(f"/admin/task/edit/?id={new_id}", data={
        "csrf_token": token,
        "task": "Admin-created",
        "base_points": "5",
        "time_factor": "0",
        "state": "1",
        "todo_time": "",
        "last_done": "",
        "schedule_days": "",
    })
    assert r.status_code == 302, r.data
    assert db_query(lambda: Task.get(Task.id == new_id).state) == Task.TODO
