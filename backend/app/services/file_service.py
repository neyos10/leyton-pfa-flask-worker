import re
from pathlib import Path
from urllib.parse import unquote, urlparse
from uuid import uuid4

import requests


DOWNLOADS_DIR = Path("downloads")
DOWNLOAD_TIMEOUT_SECONDS = 10


class DownloadFileError(Exception):
    pass


def _filename_from_url(url):
    parsed_url = urlparse(url)
    filename = unquote(Path(parsed_url.path).name)
    filename = re.sub(r"[^A-Za-z0-9._-]", "_", filename).strip("._")

    if not filename:
        filename = "downloaded_file"

    return f"{uuid4().hex}_{filename}"


def download_file(url):
    if not isinstance(url, str) or not url.strip():
        raise DownloadFileError("Invalid URL: a non-empty URL is required")

    clean_url = url.strip()
    parsed_url = urlparse(clean_url)

    if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
        raise DownloadFileError("Invalid URL: expected a valid http or https URL")

    try:
        response = requests.get(clean_url, timeout=DOWNLOAD_TIMEOUT_SECONDS)
    except requests.exceptions.Timeout as error:
        raise DownloadFileError(
            f"Download timed out after {DOWNLOAD_TIMEOUT_SECONDS} seconds"
        ) from error
    except requests.exceptions.InvalidURL as error:
        raise DownloadFileError("Invalid URL: requests could not parse the URL") from error
    except requests.exceptions.RequestException as error:
        raise DownloadFileError(f"Download failed: {error}") from error

    if response.status_code != 200:
        raise DownloadFileError(
            f"Download failed: HTTP status {response.status_code}"
        )

    DOWNLOADS_DIR.mkdir(exist_ok=True)
    local_path = DOWNLOADS_DIR / _filename_from_url(clean_url)

    try:
        local_path.write_bytes(response.content)
    except OSError as error:
        raise DownloadFileError(f"Could not save downloaded file: {error}") from error

    return str(local_path)
