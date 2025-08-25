import hashlib
import base64
from typing import Union
from app.core.logger import get_logger

logger = get_logger(__name__)


def hash_text(text: str) -> str:
    """
    Generate SHA-256 hash for text content.
    Normalizes whitespace and case before hashing.
    """
    try:
        normalized_text = " ".join(text.strip().lower().split())
        return hashlib.sha256(normalized_text.encode("utf-8")).hexdigest()
    except Exception as e:
        logger.error("Error hashing text", error=str(e))
        raise


def hash_image(image_data: Union[str, bytes]) -> str:
    """
    Generate SHA-256 hash for image bytes or base64 string.
    """
    try:
        if isinstance(image_data, str):
            if image_data.startswith("data:image"):
                image_data = image_data.split(",", 1)[1]
            image_bytes = base64.b64decode(image_data)
        else:
            image_bytes = image_data
        return hashlib.sha256(image_bytes).hexdigest()
    except Exception as e:
        logger.error("Error hashing image", error=str(e))
        raise


def hash_url(url: str) -> str:
    """
    Generate SHA-256 hash for a URL (lowercased, trimmed).
    """
    try:
        normalized_url = url.strip().lower()
        return hashlib.sha256(normalized_url.encode("utf-8")).hexdigest()
    except Exception as e:
        logger.error("Error hashing URL", error=str(e))
        raise


