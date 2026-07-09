import time

import pandas as pd

from app import create_app, db
from app.models.task import Task
from app.services.elasticsearch_service import (
    index_merged_result,
    index_task,
    search_by_code,
)
from app.services.file_service import DownloadFileError, download_file
from app.services.merge_service import get_merge_strategy


def _commit_and_index_task(task):
    db.session.commit()

    try:
        index_task(task)
    except Exception as error:
        print(
            f"Task {task.id} Elasticsearch sync failed: {error}",
            flush=True,
        )


def _process_downloaded_csv(task, local_file_path):
    dataframe = pd.read_csv(local_file_path, dtype=str).fillna("")

    if "code" not in dataframe.columns:
        print(
            f"Task {task.id} CSV has no 'code' column; skipping merge",
            flush=True,
        )
        return

    merge_strategy = get_merge_strategy()

    for row_index, row in dataframe.iterrows():
        try:
            csv_row = row.to_dict()
            code = str(csv_row.get("code", "")).strip()

            if not code:
                print(
                    f"Task {task.id} row {row_index} has no code; skipping",
                    flush=True,
                )
                continue

            es_data = search_by_code(code)
            merged_doc = merge_strategy.merge(csv_row, es_data)
            doc_id = f"{task.id}-{row_index}"
            index_merged_result(merged_doc, doc_id)
        except Exception as error:
            print(
                f"Task {task.id} row {row_index} merge failed: {error}",
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
                _process_downloaded_csv(task, local_file_path)

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
