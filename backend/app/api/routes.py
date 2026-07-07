from flask import Blueprint, jsonify, request

from app import db
from app.api.schemas import validate_task_payload
from app.models.task import Task


api_bp = Blueprint("api_bp", __name__)

ALLOWED_STATUSES = {"pending", "in_progress", "done", "failed"}


@api_bp.post("/tasks")
def create_task():
    data = request.get_json(silent=True) or {}
    errors = validate_task_payload(data)

    if errors:
        return jsonify({"errors": errors}), 400

    task = Task(
        file_location=data["file_location"],
        parameters=data.get("parameters"),
    )
    db.session.add(task)
    db.session.commit()

    return jsonify(task.to_dict()), 201


@api_bp.get("/tasks/<int:task_id>")
def get_task(task_id):
    task = db.session.get(Task, task_id)

    if task is None:
        return jsonify({"message": "Task not found"}), 404

    return jsonify(task.to_dict())


@api_bp.get("/tasks")
def list_tasks():
    status = request.args.get("status")
    query = Task.query

    if status:
        query = query.filter_by(status=status)

    tasks = query.all()

    return jsonify([task.to_dict() for task in tasks])


@api_bp.patch("/tasks/<int:task_id>")
def update_task_status(task_id):
    task = db.session.get(Task, task_id)

    if task is None:
        return jsonify({"message": "Task not found"}), 404

    data = request.get_json(silent=True) or {}
    status = data.get("status")

    if status not in ALLOWED_STATUSES:
        return jsonify({"errors": ["Invalid status"]}), 400

    task.status = status
    db.session.commit()

    return jsonify(task.to_dict())
