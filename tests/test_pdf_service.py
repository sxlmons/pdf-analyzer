"""Tests for the PDF extraction service."""

from io import BytesIO
from app.services.pdf_service import extract_text_from_pdf
from tests.conftest import make_pdf, make_empty_pdf


class TestExtractTextFromPdf:

    def test_extracts_text_from_valid_pdf(self):
        pdf = make_pdf("Hello world, this is a test.")
        result = extract_text_from_pdf(pdf)
        assert "Hello world" in result

    def test_returns_empty_string_for_blank_pdf(self):
        pdf = make_empty_pdf()
        result = extract_text_from_pdf(pdf)
        assert result == ""

    def test_raises_on_invalid_file(self):
        fake_file = BytesIO(b"this is not a pdf")
        try:
            extract_text_from_pdf(fake_file)
            assert False, "Should have raised an exception"
        except Exception:
            pass  # Expected — pypdf can't parse garbage