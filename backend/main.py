import threading
import traceback

from app import create_app
from app.worker.worker import run_worker


def _run_worker():
    try:
        run_worker()
    except Exception as error:
        print(f"Worker thread stopped after an unexpected error: {error}", flush=True)
        traceback.print_exc()


def main():
    print("Starting Flask API and worker in the same process", flush=True)

    worker_thread = threading.Thread(
        target=_run_worker,
        name="worker",
        daemon=True,
    )
    worker_thread.start()

    app = create_app()
    app.run(host="0.0.0.0", port=5000)


if __name__ == "__main__":
    main()
