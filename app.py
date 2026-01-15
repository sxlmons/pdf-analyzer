import os
from io import BytesIO

from flask import Flask, request, render_template, session
from dotenv import load_dotenv
import google.generativeai as genai
from pypdf import PdfReader

# Load environment variables from .env file
load_dotenv()

# Configure Gemini with your API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)  # Required for session management

# Hidden system prompt - user never sees this but it shapes all responses
SYSTEM_PROMPT = """You are an advanced PhD-level specialist with expertise across multiple academic disciplines. 
Analyze documents thoroughly, cite specific sections when relevant, and provide clear, well-structured responses. 
Be precise but accessible. When summarizing or answering questions about a document, ground your response 
in the actual content provided. Use markdown formatting for better readability."""


def extract_text_from_pdf(pdf_file):
    """
    Takes an uploaded PDF file and extracts all text content.
    Returns the combined text from all pages.
    """
    reader = PdfReader(BytesIO(pdf_file.read()))
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text.strip()


def analyze_with_gemini(document_text, conversation_history):
    """
    Sends the document + full conversation history to Gemini.
    Returns the assistant's response.
    """
    # Build the full prompt with document context and conversation history
    messages = f"""{SYSTEM_PROMPT}

--- DOCUMENT CONTENT ---
{document_text}
--- END DOCUMENT ---

Below is the conversation so far. Continue naturally from here.

"""
    # Add conversation history
    for msg in conversation_history:
        role = "User" if msg["role"] == "user" else "Assistant"
        messages += f"{role}: {msg['content']}\n\n"

    messages += "Assistant: "

    # Call Gemini API
    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(messages)

    return response.text


@app.route("/")
def index():
    """Serve the main page. Show chat if document is loaded, otherwise show upload."""
    has_document = "document_text" in session
    chat_history = session.get("chat_history", [])
    filename = session.get("filename", "")
    return render_template("index.html",
                           has_document=has_document,
                           chat_history=chat_history,
                           filename=filename)


@app.route("/upload", methods=["POST"])
def upload():
    """
    Handle PDF upload:
    1. Extract text from PDF
    2. Store in session
    3. Clear any existing chat history
    """
    pdf_file = request.files.get("pdf")

    # Validation
    if not pdf_file or pdf_file.filename == "":
        return render_template("index.html", error="Please upload a PDF file.", has_document=False)

    if not pdf_file.filename.lower().endswith(".pdf"):
        return render_template("index.html", error="Only PDF files are supported.", has_document=False)

    try:
        # Extract text from the PDF
        document_text = extract_text_from_pdf(pdf_file)

        if not document_text:
            return render_template("index.html",
                                   error="Could not extract text from PDF. It may be scanned/image-based.",
                                   has_document=False)

        # Store document in session and reset chat
        session["document_text"] = document_text
        session["chat_history"] = []
        session["filename"] = pdf_file.filename

        return render_template("index.html",
                               has_document=True,
                               chat_history=[],
                               filename=pdf_file.filename)

    except Exception as e:
        return render_template("index.html", error=f"An error occurred: {str(e)}", has_document=False)


@app.route("/chat", methods=["POST"])
def chat():
    """
    Handle chat messages:
    1. Add user message to history
    2. Get response from Gemini
    3. Add assistant response to history
    """
    # Check if document is loaded
    if "document_text" not in session:
        return render_template("index.html",
                               error="Please upload a PDF first.",
                               has_document=False)

    question = request.form.get("question", "").strip()

    if not question:
        return render_template("index.html",
                               has_document=True,
                               chat_history=session.get("chat_history", []),
                               filename=session.get("filename", ""),
                               error="Please enter a message.")

    try:
        # Add user message to history
        chat_history = session.get("chat_history", [])
        chat_history.append({"role": "user", "content": question})

        # Get response from Gemini
        response = analyze_with_gemini(session["document_text"], chat_history)

        # Add assistant response to history
        chat_history.append({"role": "assistant", "content": response})

        # Save updated history to session
        session["chat_history"] = chat_history

        return render_template("index.html",
                               has_document=True,
                               chat_history=chat_history,
                               filename=session.get("filename", ""))

    except Exception as e:
        return render_template("index.html",
                               has_document=True,
                               chat_history=session.get("chat_history", []),
                               filename=session.get("filename", ""),
                               error=f"An error occurred: {str(e)}")


@app.route("/reset", methods=["POST"])
def reset():
    """Clear the session and start fresh."""
    session.clear()
    return render_template("index.html", has_document=False, chat_history=[])


if __name__ == "__main__":
    app.run(debug=True)