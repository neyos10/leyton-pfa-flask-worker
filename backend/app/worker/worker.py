import time

from app import create_app, db
from app.models.task import Task
from app.services.elasticsearch_service import index_task
from app.services.file_service import DownloadFileError, download_file


def _commit_and_index_task(task):
    db.session.commit()

    try:
        index_task(task)
    except Exception as error:
        print(
            f"Task {task.id} Elasticsearch sync failed: {error}",
            flush=True,
        )


def process_pending_tasks(app=None):
    app = app or create_app()

    with app.app_context():
        pending_tasks = Task.query.filter_by(status="pending").all()

        for task in pending_tasks:
            try:
                task.status = "in_progress"
                _commit_and_index_task(task)

                print(
                    f"Processing task {task.id}: {task.file_location}",
                    flush=True,
                )

                local_file_path = download_file(task.file_location)

                task.status = "done"
                _commit_and_index_task(task)

                print(f"Task {task.id} completed: {local_file_path}", flush=True)
            except DownloadFileError as error:
                db.session.rollback()
                task.status = "failed"
                _commit_and_index_task(task)
                print(f"Task {task.id} download failed: {error}", flush=True)
            except Exception as error:
                db.session.rollback()
                task.status = "failed"
                _commit_and_index_task(task)
                print(f"Task {task.id} failed: {error}", flush=True)


def run_worker():
    app = create_app()

    while True:
        process_pending_tasks(app)
        time.sleep(5)
