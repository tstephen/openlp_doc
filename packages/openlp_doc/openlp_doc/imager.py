"""
Image processing utilities for OpenLP document generation.

This module provides the Imager class for converting images from local files
or URLs into data URLs for embedding in HTML documents.
"""

import base64
import logging
import mimetypes
from pathlib import Path
from typing import Optional, Union
from urllib.parse import urlparse
from urllib.request import urlopen

log = logging.getLogger(__name__)


class ImageError(Exception):
    """Exception raised for image processing errors."""

    pass


class Imager:
    """
    A utility class for converting images to data URLs.

    Supports both local file paths and remote URLs for JPEG and PNG images.
    """

    SUPPORTED_FORMATS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"}
    MIME_TYPES = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
        ".bmp": "image/bmp",
    }

    def __init__(self, max_file_size: int = 10 * 1024 * 1024):  # 10MB default
        """
        Initialize the Imager.

        Args:
            max_file_size: Maximum file size in bytes (default: 10MB)
        """
        self.max_file_size = max_file_size

    def to_data_url(self, source: Union[str, Path]) -> str:
        """
        Convert an image from file path or URL to a data URL.

        Args:
            source: Local file path or URL to the image

        Returns:
            Data URL string (data:image/type;base64,...)

        Raises:
            ImageError: If the image cannot be processed
        """
        try:
            if self._is_url(source):
                return self._url_to_data_url(str(source))
            else:
                return self._file_to_data_url(Path(source))
        except Exception as e:
            raise ImageError(f"Failed to process image '{source}': {e}") from e

    def _is_url(self, source: Union[str, Path]) -> bool:
        """Check if the source is a URL."""
        source_str = str(source)
        parsed = urlparse(source_str)
        return parsed.scheme in ("http", "https")

    def _file_to_data_url(self, file_path: Path) -> str:
        """
        Convert a local image file to a data URL.

        Args:
            file_path: Path to the local image file

        Returns:
            Data URL string

        Raises:
            ImageError: If file cannot be read or is invalid
        """
        if not file_path.exists():
            raise ImageError(f"File does not exist: {file_path}")

        if not file_path.is_file():
            raise ImageError(f"Path is not a file: {file_path}")

        # Check file size
        file_size = file_path.stat().st_size
        if file_size > self.max_file_size:
            raise ImageError(
                f"File size ({file_size} bytes) exceeds maximum "
                f"({self.max_file_size} bytes)"
            )

        # Check file extension
        suffix = file_path.suffix.lower()
        if suffix not in self.SUPPORTED_FORMATS:
            raise ImageError(f"Unsupported image format: {suffix}")

        # Determine MIME type
        mime_type = self.MIME_TYPES.get(suffix)
        if not mime_type:
            # Fallback to mimetypes module
            mime_type, _ = mimetypes.guess_type(str(file_path))
            if not mime_type or not mime_type.startswith("image/"):
                raise ImageError(
                    f"Cannot determine MIME type for: {file_path}"
                )

        # Read and encode the file
        try:
            with open(file_path, "rb") as f:
                image_data = f.read()
        except IOError as e:
            raise ImageError(f"Cannot read file {file_path}: {e}")

        # Encode as base64
        base64_data = base64.b64encode(image_data).decode("ascii")

        # Create data URL
        data_url = f"data:{mime_type};base64,{base64_data}"

        log.info(
            f"Converted local image {file_path} to data URL "
            f"({len(base64_data)} chars)"
        )

        return data_url

    def _url_to_data_url(self, url: str) -> str:
        """
        Convert an image URL to a data URL.

        Args:
            url: HTTP(S) URL to the image

        Returns:
            Data URL string

        Raises:
            ImageError: If URL cannot be fetched or is invalid
        """
        log.info(f"Fetching image from URL: {url}")

        try:
            with urlopen(url) as response:
                # Check content length
                content_length = response.headers.get("Content-Length")
                if content_length:
                    size = int(content_length)
                    if size > self.max_file_size:
                        raise ImageError(
                            f"Image size ({size} bytes) exceeds maximum "
                            f"({self.max_file_size} bytes)"
                        )

                # Check content type
                content_type = response.headers.get("Content-Type", "")
                if not content_type.startswith("image/"):
                    raise ImageError(
                        f"URL does not point to an image: {content_type}"
                    )

                # Read the image data
                image_data = response.read()

                # Double-check size after reading
                if len(image_data) > self.max_file_size:
                    raise ImageError(
                        f"Downloaded image size ({len(image_data)} bytes) "
                        f"exceeds maximum ({self.max_file_size} bytes)"
                    )

        except Exception as e:
            if isinstance(e, ImageError):
                raise
            raise ImageError(f"Cannot fetch image from URL {url}: {e}")

        # Encode as base64
        base64_data = base64.b64encode(image_data).decode("ascii")

        # Create data URL
        data_url = f"data:{content_type};base64,{base64_data}"

        log.info(f"Converted URL {url} to data URL ({len(base64_data)} chars)")

        return data_url

    def bytes_to_data_url(
        self, image_bytes: bytes, file_extension: str
    ) -> str:
        """
        Convert image bytes to a data URL.

        Args:
            image_bytes: Raw image data as bytes
            file_extension: File extension to determine MIME type

        Returns:
            Data URL string

        Raises:
            ImageError: If the image data is invalid
        """
        if not image_bytes:
            raise ImageError("No image data provided")

        # Check file size
        if len(image_bytes) > self.max_file_size:
            raise ImageError(
                f"Image size ({len(image_bytes)} bytes) exceeds maximum "
                f"({self.max_file_size} bytes)"
            )

        # Check file extension
        suffix = file_extension.lower()
        if not suffix.startswith("."):
            suffix = "." + suffix

        if suffix not in self.SUPPORTED_FORMATS:
            raise ImageError(f"Unsupported image format: {suffix}")

        # Determine MIME type
        mime_type = self.MIME_TYPES.get(suffix)
        if not mime_type:
            raise ImageError(f"Cannot determine MIME type for: {suffix}")

        # Encode as base64
        base64_data = base64.b64encode(image_bytes).decode("ascii")

        # Create data URL
        data_url = f"data:{mime_type};base64,{base64_data}"

        log.info(
            f"Converted image bytes to data URL ({len(base64_data)} chars)"
        )

        return data_url

    def get_image_info(self, source: Union[str, Path]) -> dict:
        """
        Get information about an image without converting it.

        Args:
            source: Local file path or URL to the image

        Returns:
            Dictionary with image information (size, type, etc.)

        Raises:
            ImageError: If the image cannot be accessed
        """
        try:
            if self._is_url(source):
                return self._get_url_info(str(source))
            else:
                return self._get_file_info(Path(source))
        except Exception as e:
            raise ImageError(
                f"Failed to get image info for '{source}': {e}"
            ) from e

    def _get_file_info(self, file_path: Path) -> dict:
        """Get information about a local image file."""
        if not file_path.exists():
            raise ImageError(f"File does not exist: {file_path}")

        stat = file_path.stat()
        suffix = file_path.suffix.lower()

        return {
            "source": str(file_path),
            "type": "file",
            "size": stat.st_size,
            "extension": suffix,
            "mime_type": self.MIME_TYPES.get(suffix),
            "supported": suffix in self.SUPPORTED_FORMATS,
            "modified": stat.st_mtime,
        }

    def _get_url_info(self, url: str) -> dict:
        """Get information about an image URL."""
        try:
            with urlopen(url) as response:
                content_type = response.headers.get("Content-Type", "")
                content_length = response.headers.get("Content-Length")

                return {
                    "source": url,
                    "type": "url",
                    "size": int(content_length) if content_length else None,
                    "mime_type": content_type,
                    "supported": content_type.startswith("image/"),
                    "status_code": response.getcode(),
                }
        except Exception as e:
            raise ImageError(f"Cannot access URL {url}: {e}")
