import time

from app import create_app, db
from app.models.task import Task
from app.services.file_service import DownloadFileError, download_file


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

                    local_file_path = download_file(task.file_location)

                    task.status = "done"
                    db.session.commit()

                    print(f"Task {task.id} completed: {local_file_path}", flush=True)
                except DownloadFileError as error:
                    db.session.rollback()
                    task.status = "failed"
                    db.session.commit()
                    print(f"Task {task.id} download failed: {error}", flush=True)
                except Exception as error:
                    db.session.rollback()
                    task.status = "failed"
                    db.session.commit()
                    print(f"Task {task.id} failed: {error}", flush=True)

            time.sleep(5)
