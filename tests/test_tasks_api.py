import pytest

from app import create_app, db
from app.models.task import Task


@pytest.fixture()
def app(tmp_path):
    database_path = tmp_path / "tasks_test.db"
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{database_path}",
        }
    )

    yield app

    with app.app_context():
        db.session.remove()
        Task.__table__.drop(db.engine, checkfirst=True)


@pytest.fixture()
def client(app):
    return app.test_client()


def test_create_task(client):
    response = client.post(
        "/tasks",
        json={
            "file_location": "/tmp/document.pdf",
            "parameters": {"source": "pytest"},
        },
    )

    assert response.status_code == 201
    data = response.get_json()
    assert data["id"] == 1
    assert data["file_location"] == "/tmp/document.pdf"
    assert data["status"] == "pending"
    assert data["parameters"] == {"source": "pytest"}
    assert isinstance(data["created_at"], str)
    assert isinstance(data["updated_at"], str)


def test_create_task_requires_file_location(client):
    response = client.post("/tasks", json={"file_location": "   "})

    assert response.status_code == 400
    assert response.get_json() == {"errors": ["file_location is required"]}


def test_get_task_by_id(client):
    create_response = client.post("/tasks", json={"file_location": "/tmp/report.pdf"})
    task_id = create_response.get_json()["id"]

    response = client.get(f"/tasks/{task_id}")

    assert response.status_code == 200
    assert response.get_json()["file_location"] == "/tmp/report.pdf"


def test_get_missing_task_returns_404(client):
    response = client.get("/tasks/999")

    assert response.status_code == 404
    assert response.get_json() == {"message": "Task not found"}


def test_list_tasks_can_filter_by_status(client):
    first = client.post("/tasks", json={"file_location": "/tmp/first.pdf"}).get_json()
    second = client.post("/tasks", json={"file_location": "/tmp/second.pdf"}).get_json()
    client.patch(f"/tasks/{second['id']}", json={"status": "done"})

    response = client.get("/tasks?status=done")

    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]["id"] == second["id"]
    assert data[0]["status"] == "done"
    assert data[0]["id"] != first["id"]


def test_patch_task_status(client):
    create_response = client.post("/tasks", json={"file_location": "/tmp/task.pdf"})
    task_id = create_response.get_json()["id"]

    response = client.patch(f"/tasks/{task_id}", json={"status": "in_progress"})

    assert response.status_code == 200
    assert response.get_json()["status"] == "in_progress"


def test_patch_task_rejects_invalid_status(client):
    create_response = client.post("/tasks", json={"file_location": "/tmp/task.pdf"})
    task_id = create_response.get_json()["id"]

    response = client.patch(f"/tasks/{task_id}", json={"status": "unknown"})

    assert response.status_code == 400
    assert response.get_json() == {"errors": ["Invalid status"]}
