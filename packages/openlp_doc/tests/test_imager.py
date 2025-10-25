"""
Tests for the Imager class
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest

from openlp_doc.imager import ImageError, Imager


class TestImager:
    """Test cases for the Imager class"""

    def test_init_default(self):
        """Test Imager initialization with defaults"""
        imager = Imager()
        assert imager.max_file_size == 10 * 1024 * 1024  # 10MB

    def test_init_custom_size(self):
        """Test Imager initialization with custom max size"""
        custom_size = 5 * 1024 * 1024  # 5MB
        imager = Imager(max_file_size=custom_size)
        assert imager.max_file_size == custom_size

    def test_is_url(self):
        """Test URL detection"""
        imager = Imager()

        # Valid URLs
        assert imager._is_url("http://example.com/image.jpg") is True
        assert imager._is_url("https://example.com/image.png") is True

        # File paths
        assert imager._is_url("/path/to/image.jpg") is False
        assert imager._is_url("image.png") is False
        assert imager._is_url(Path("image.jpg")) is False

    def test_supported_formats(self):
        """Test supported format checking"""
        imager = Imager()

        # Check that common formats are supported
        assert ".jpg" in imager.SUPPORTED_FORMATS
        assert ".jpeg" in imager.SUPPORTED_FORMATS
        assert ".png" in imager.SUPPORTED_FORMATS
        assert ".gif" in imager.SUPPORTED_FORMATS

    def test_mime_types(self):
        """Test MIME type mapping"""
        imager = Imager()

        assert imager.MIME_TYPES[".jpg"] == "image/jpeg"
        assert imager.MIME_TYPES[".jpeg"] == "image/jpeg"
        assert imager.MIME_TYPES[".png"] == "image/png"

    def test_file_not_exists(self):
        """Test error when file doesn't exist"""
        imager = Imager()

        with pytest.raises(ImageError, match="File does not exist"):
            imager.to_data_url("/nonexistent/file.jpg")

    def test_file_too_large(self):
        """Test error when file is too large"""
        imager = Imager(max_file_size=100)  # Very small limit

        with tempfile.NamedTemporaryFile(
            suffix=".jpg", delete=False
        ) as tmp_file:
            # Write data larger than limit
            tmp_file.write(b"x" * 200)
            tmp_file.flush()

            try:
                with pytest.raises(ImageError, match="exceeds maximum"):
                    imager.to_data_url(tmp_file.name)
            finally:
                Path(tmp_file.name).unlink()

    def test_unsupported_format(self):
        """Test error with unsupported file format"""
        imager = Imager()

        with tempfile.NamedTemporaryFile(
            suffix=".txt", delete=False
        ) as tmp_file:
            tmp_file.write(b"not an image")
            tmp_file.flush()

            try:
                with pytest.raises(
                    ImageError, match="Unsupported image format"
                ):
                    imager.to_data_url(tmp_file.name)
            finally:
                Path(tmp_file.name).unlink()

    @patch(
        "builtins.open", new_callable=mock_open, read_data=b"\x89PNG\r\n\x1a\n"
    )
    @patch("pathlib.Path.exists", return_value=True)
    @patch("pathlib.Path.is_file", return_value=True)
    @patch("pathlib.Path.stat")
    def test_file_to_data_url_success(
        self, mock_stat, mock_is_file, mock_exists, mock_file
    ):
        """Test successful file to data URL conversion"""
        # Mock file stats
        mock_stat.return_value.st_size = 100

        imager = Imager()

        # Test with PNG file
        result = imager._file_to_data_url(Path("/test/image.png"))

        # Should return a data URL
        assert result.startswith("data:image/png;base64,")
        assert len(result) > len("data:image/png;base64,")

    @patch("openlp_doc.imager.urlopen")
    def test_url_to_data_url_success(self, mock_urlopen):
        """Test successful URL to data URL conversion"""
        # Mock HTTP response
        mock_response = MagicMock()
        mock_response.headers = {
            "Content-Type": "image/jpeg",
            "Content-Length": "1000",
        }
        mock_response.read.return_value = b"\xff\xd8\xff\xe0"  # JPEG header
        mock_urlopen.return_value.__enter__.return_value = mock_response

        imager = Imager()
        result = imager._url_to_data_url("https://example.com/image.jpg")

        # Should return a data URL
        assert result.startswith("data:image/jpeg;base64,")
        mock_urlopen.assert_called_once_with("https://example.com/image.jpg")

    @patch("openlp_doc.imager.urlopen")
    def test_url_too_large(self, mock_urlopen):
        """Test error when URL image is too large"""
        # Mock HTTP response with large content
        mock_response = MagicMock()
        mock_response.headers = {
            "Content-Type": "image/jpeg",
            "Content-Length": str(20 * 1024 * 1024),  # 20MB
        }
        mock_urlopen.return_value.__enter__.return_value = mock_response

        imager = Imager()

        with pytest.raises(ImageError, match="Image size .* exceeds maximum"):
            imager._url_to_data_url("https://example.com/large-image.jpg")

    @patch("openlp_doc.imager.urlopen")
    def test_url_not_image(self, mock_urlopen):
        """Test error when URL doesn't point to an image"""
        # Mock HTTP response with non-image content
        mock_response = MagicMock()
        mock_response.headers = {"Content-Type": "text/html"}
        mock_urlopen.return_value.__enter__.return_value = mock_response

        imager = Imager()

        with pytest.raises(ImageError, match="URL does not point to an image"):
            imager._url_to_data_url("https://example.com/page.html")

    def test_get_image_info_file_not_exists(self):
        """Test get_image_info with non-existent file"""
        imager = Imager()

        with pytest.raises(ImageError, match="File does not exist"):
            imager.get_image_info("/nonexistent/file.jpg")


if __name__ == "__main__":
    # Run a simple test
    imager = Imager()

    # Test URL detection
    print("Testing URL detection...")
    assert imager._is_url("https://example.com/image.jpg") is True
    assert imager._is_url("/local/path.jpg") is False
    print("✓ URL detection works")

    # Test supported formats
    print("Testing supported formats...")
    assert ".jpg" in imager.SUPPORTED_FORMATS
    assert ".png" in imager.SUPPORTED_FORMATS
    print("✓ Supported formats correct")

    print("Basic tests passed!")
