"""Image sanitization utilities for user uploads.

Validates, normalizes orientation, strips metadata, converts to safe format,
and resizes to a bounded box.

Dependencies: Pillow
"""
from __future__ import annotations

import io
import os
from typing import Tuple, Optional

try:
    from PIL import Image, ImageOps, ImageFile
    HAS_PILLOW = True
except Exception:  # pragma: no cover - Pillow missing
    Image = None  # type: ignore
    ImageOps = None  # type: ignore
    ImageFile = None  # type: ignore
    HAS_PILLOW = False

# Optional Rust service integration
try:
    import requests  # type: ignore
    _HAS_REQUESTS = True
except Exception:  # pragma: no cover
    requests = None  # type: ignore
    _HAS_REQUESTS = False


# Guard against decompression bombs
try:
    if HAS_PILLOW:
        Image.MAX_IMAGE_PIXELS = 30_000_000  # ~30MP
except Exception:
    pass


class ImageSanitizationError(Exception):
    pass


def sanitize_image(
    file_bytes: bytes,
    max_size: Tuple[int, int] = (256, 256),
    out_format: str = "WEBP",
    quality: int = 85,
) -> Tuple[bytes, str, Tuple[int, int]]:
    """
    Sanitize an uploaded image.

    - Ensures it's a real image (opens with Pillow)
    - Applies EXIF orientation
    - Converts to RGB/RGBA as needed
    - Strips metadata
    - Resizes to fit within max_size, preserving aspect ratio (no upscale)
    - Saves as out_format (WEBP or PNG)

    Returns: (bytes_data, extension_without_dot, (width, height))
    """
    # Try Rust microservice first if configured
    rust_url = os.environ.get("RUST_IMAGES_URL")
    if rust_url and _HAS_REQUESTS:
        try:
            resp = requests.post(rust_url.rstrip('/') + '/sanitize', files={"file": ("upload", file_bytes) }, timeout=10)
            if resp.ok and resp.content:
                ct = (resp.headers.get('Content-Type') or '').lower()
                ext = 'webp' if 'webp' in ct else ('png' if 'png' in ct else 'webp')
                # No dimension data from service; return (0,0) as placeholder
                return resp.content, ext, (0, 0)
        except Exception:
            # fall back to Pillow
            pass

    if not HAS_PILLOW:
        raise ImageSanitizationError("Pillow not installed and Rust service unavailable")

    if not file_bytes or len(file_bytes) == 0:
        raise ImageSanitizationError("Empty file")

    # Some truncated files can crash decoders; avoid loading truncated images
    try:
        ImageFile.LOAD_TRUNCATED_IMAGES = False
    except Exception:
        pass

    try:
        with Image.open(io.BytesIO(file_bytes)) as im:
            im.load()  # validate by decoding
            # Normalize orientation
            im = ImageOps.exif_transpose(im)

            # Convert to RGB (drop alpha unless saving to PNG or WEBP supports alpha)
            save_params = {}
            fmt = out_format.upper()
            if fmt == "PNG":
                if im.mode not in ("RGB", "RGBA"):
                    im = im.convert("RGBA") if "A" in im.getbands() else im.convert("RGB")
            else:  # WEBP
                # WEBP supports alpha; convert appropriately
                if im.mode not in ("RGB", "RGBA"):
                    im = im.convert("RGBA") if "A" in im.getbands() else im.convert("RGB")
                save_params.update({"quality": int(quality), "method": 6})

            # Resize if needed (contain within box)
            max_w, max_h = max_size
            if im.width > max_w or im.height > max_h:
                im.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)

            out = io.BytesIO()
            if fmt == "PNG":
                im.save(out, format="PNG", optimize=True)
                ext = "png"
            else:
                im.save(out, format="WEBP", **save_params)
                ext = "webp"
            data = out.getvalue()
            return data, ext, (im.width, im.height)
    except ImageSanitizationError:
        raise
    except Exception as e:
        raise ImageSanitizationError(f"Invalid or unsupported image: {e}")


def is_allowed_mime(mime: Optional[str]) -> bool:
    if not mime:
        return False
    mime = mime.lower()
    return mime in (
        "image/jpeg",
        "image/jpg",
        "image/png",
        "image/webp",
        "image/gif",
    )
