import tempfile
import os

from fastapi import UploadFile


def save_upload_file_to_temp(upload_file: UploadFile) -> str:
    """Save UploadFile to a temp file and return the path."""
    suffix = os.path.splitext(upload_file.filename or "")[1] or ".wav"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = upload_file.file.read()
        tmp.write(content)
        return tmp.name


def clean_text(text: str) -> str:
    if not text:
        return ""
    return text.strip()
