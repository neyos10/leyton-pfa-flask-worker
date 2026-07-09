def validate_task_payload(data):
    errors = []
    file_location = data.get("file_location") if isinstance(data, dict) else None

    if not file_location or not str(file_location).strip():
        errors.append("file_location is required")

    return errors
