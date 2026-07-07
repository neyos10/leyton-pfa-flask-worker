import time

from app import create_app, db
from app.models.task import Task


def run_worker():
    app = create_app()

    with app.app_context():
        while True:
            pending_tasks = Task.query.filter_by(status="pending").all()

            for task in pending_tasks:
                try:
                    task.status = "in_progress"
                    db.session.commit()

                    print(
                        f"Processing task {task.id}: {task.file_location}",
                        flush=True,
                    )

                    time.sleep(2)

                    task.status = "done"
                    db.session.commit()

                    print(f"Task {task.id} completed", flush=True)
                except Exception as error:
                    db.session.rollback()
                    task.status = "failed"
                    db.session.commit()
                    print(f"Task {task.id} failed: {error}", flush=True)

            time.sleep(5)
