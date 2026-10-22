"""Validated image storage for RenewGrid."""
import io
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile
from PIL import Image, ImageOps, UnidentifiedImageError

UPLOAD_ROOT = Path("uploads")
MAX_UPLOAD_BYTES = 5 * 1024 * 1024
MAX_IMAGE_PIXELS = 12_000_000
ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP", "GIF"}
ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
}
ALLOWED_FOLDERS = {
    "waste",
    "proofs",
    "profile_images",
}

# Guard against decompression-bomb attacks (Pillow default is 178M).
Image.MAX_IMAGE_PIXELS = MAX_IMAGE_PIXELS


def prepare_image(file: UploadFile) -> bytes:
    """Validate, decode and normalize an image to PNG bytes.

    Raises HTTPException 400/413 on validation failure.
    Returns raw PNG bytes ready to be persisted.
    """
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported file type '{file.content_type}'. "
                f"Allowed: {sorted(ALLOWED_CONTENT_TYPES)}"
            ),
        )

    raw = file.file.read()
    if len(raw) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail="File too large. Maximum size is 5 MB.",
        )

    try:
        img = Image.open(io.BytesIO(raw))
        # Verify that the image can actually be decoded (catches polyglot files).
        img.verify()
        # Re-open after verify() (which exhausts the file object).
        img = Image.open(io.BytesIO(raw))
        img = img.convert("RGBA") if img.mode in ("RGBA", "LA") else img.convert("RGB")
        # Auto-correct EXIF orientation before stripping metadata.
        img = ImageOps.exif_transpose(img)
    except UnidentifiedImageError:
        raise HTTPException(
            status_code=400,
            detail="File could not be identified as a valid image.",
        )
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Image processing failed. Please upload a valid image file.",
        )

    # Re-encode to PNG — strips EXIF metadata and enforces a known format.
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


def save_prepared_image(png_bytes: bytes, folder: str) -> str:
    """Persist prepared PNG bytes under UPLOAD_ROOT/folder and return the URL path."""
    if folder not in ALLOWED_FOLDERS:
        raise ValueError(f"Unknown upload folder: {folder!r}")

    dest_dir = UPLOAD_ROOT / folder
    dest_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{uuid.uuid4().hex}.png"
    dest = dest_dir / filename
    dest.write_bytes(png_bytes)
    return f"/uploads/{folder}/{filename}"


def delete_uploaded_path(path: str | None) -> None:
    """Best-effort deletion of a stored upload path. Never raises."""
    if not path:
        return
    try:
        # Strip leading slash to build a relative path from UPLOAD_ROOT.
        relative = path.lstrip("/")
        file_path = Path(relative)
        if file_path.exists():
            file_path.unlink()
    except Exception:
        pass
