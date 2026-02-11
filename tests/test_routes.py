"""Tests for all Flask routes. Gemini API is mocked throughout."""

from io import BytesIO
from unittest.mock import patch
from tests.conftest import make_pdf


class TestIndexRoute:

    def test_shows_upload_form_when_no_document(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert b"Upload" in response.data

    def test_shows_chat_when_document_loaded(self, client):
        pdf = make_pdf("Test content")
        client.post("/upload", data={"pdf": (pdf, "test.pdf")},
                     content_type="multipart/form-data")

        response = client.get("/")
        assert response.status_code == 200
        assert b"test.pdf" in response.data


class TestUploadRoute:

    def test_rejects_missing_file(self, client):
        response = client.post("/upload", data={},
                               content_type="multipart/form-data")
        assert b"Please upload a PDF file" in response.data

    def test_rejects_non_pdf_file(self, client):
        fake = BytesIO(b"not a pdf")
        response = client.post("/upload", data={"pdf": (fake, "notes.txt")},
                               content_type="multipart/form-data")
        assert b"Only PDF files are supported" in response.data

    def test_rejects_empty_text_pdf(self, client):
        from tests.conftest import make_empty_pdf
        pdf = make_empty_pdf()
        response = client.post("/upload", data={"pdf": (pdf, "blank.pdf")},
                               content_type="multipart/form-data")
        assert b"Could not extract text" in response.data

    def test_successful_upload(self, client):
        """A valid PDF should be accepted and the chat UI should appear."""
        pdf = make_pdf("Some real content here")
        response = client.post("/upload", data={"pdf": (pdf, "report.pdf")},
                               content_type="multipart/form-data")
        assert response.status_code == 200
        assert b"report.pdf" in response.data


class TestChatRoute:

    def test_rejects_chat_without_document(self, client):
        response = client.post("/chat", data={"question": "hello"})
        assert b"Please upload a PDF first" in response.data

    def test_rejects_empty_message(self, client):
        pdf = make_pdf("Content")
        client.post("/upload", data={"pdf": (pdf, "test.pdf")},
                     content_type="multipart/form-data")

        response = client.post("/chat", data={"question": "   "})
        assert b"Please enter a message" in response.data

    @patch("app.routes.get_response", return_value="This document is about testing.")
    def test_successful_chat(self, mock_gemini, client):
        """A valid question should return the mocked AI response."""
        pdf = make_pdf("Content about testing")
        client.post("/upload", data={"pdf": (pdf, "test.pdf")},
                     content_type="multipart/form-data")

        response = client.post("/chat", data={"question": "What is this about?"})
        assert response.status_code == 200
        assert b"What is this about?" in response.data
        assert b"This document is about testing." in response.data

    @patch("app.routes.get_response", return_value="First answer.")
    def test_conversation_history_persists(self, mock_gemini, client):
        """Multiple messages should all appear in the chat."""
        pdf = make_pdf("Content")
        client.post("/upload", data={"pdf": (pdf, "test.pdf")},
                     content_type="multipart/form-data")

        client.post("/chat", data={"question": "First question"})

        mock_gemini.return_value = "Second answer."
        response = client.post("/chat", data={"question": "Follow up"})

        assert b"First question" in response.data
        assert b"Follow up" in response.data


class TestResetRoute:

    def test_reset_clears_session(self, client):
        """After reset, the upload form should be shown again."""
        pdf = make_pdf("Content")
        client.post("/upload", data={"pdf": (pdf, "test.pdf")},
                     content_type="multipart/form-data")

        response = client.post("/reset", follow_redirects=True)
        assert response.status_code == 200
        # Should be back to the upload form, no filename visible
        assert b"test.pdf" not in response.data