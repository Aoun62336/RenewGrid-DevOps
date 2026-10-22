"""Controlled serving of RenewGrid uploaded media."""
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from app.core.media_security import (
    MEDIA_PATH_PATTERN,
    PRIVATE_FOLDERS,
    verify_media_token,
)
from app.core.upload_security import UPLOAD_ROOT

router = APIRouter()

SUPPORTED_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".gif",
}


@router.get(
    "/uploads/{folder}/{filename}",
    include_in_schema=False,
)
def read_uploaded_image(
    folder: str,
    filename: str,
    token: str | None = Query(None),
):
    url_path = f"/uploads/{folder}/{filename}"

    # Reject paths that don't match the allowed pattern (prevents path traversal).
    if MEDIA_PATH_PATTERN.fullmatch(url_path) is None:
        raise HTTPException(status_code=404, detail="Not found.")

    # Require a valid signed token for private folders.
    if folder in PRIVATE_FOLDERS:
        verify_media_token(url_path, token)

    # Reject unsupported extensions even if they pass the regex.
    suffix = Path(filename).suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise HTTPException(status_code=404, detail="Not found.")

    file_path = UPLOAD_ROOT / folder / filename
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="Not found.")

    return FileResponse(
        path=str(file_path),
        headers={
            "Cache-Control": "private, max-age=900" if folder in PRIVATE_FOLDERS else "public, max-age=86400",
            "X-Content-Type-Options": "nosniff",
        },
    )
