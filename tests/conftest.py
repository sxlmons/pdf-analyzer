import pytest
from io import BytesIO
from pypdf import PdfWriter

from app import create_app
from app.config import TestConfig


@pytest.fixture
def app():
    app = create_app(TestConfig)
    yield app


@pytest.fixture
def client(app):
    """Flask test client — simulates HTTP requests without a running server."""
    return app.test_client()


def make_pdf(text="This is a test document about climate change and renewable energy."):
    """
    Helper: creates a real in-memory PDF with the given text.
    Returns a BytesIO object ready to be uploaded.
    """
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)

    # pypdf can't easily add text to pages, so we use a workaround:
    # create a PDF with reportlab if available, otherwise use a pre-built approach
    from pypdf import PdfReader
    from reportlab.pdfgen import canvas

    buf = BytesIO()
    c = canvas.Canvas(buf)
    c.drawString(72, 720, text)
    c.save()
    buf.seek(0)

    return buf


def make_empty_pdf():
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    buf = BytesIO()
    writer.write(buf)
    buf.seek(0)
    return buf