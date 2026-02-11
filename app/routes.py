from flask import Blueprint, request, render_template, session
from app.services.pdf_service import extract_text_from_pdf
from app.services.llm_service import get_response

main = Blueprint("main", __name__)


@main.route("/")
def index():
    has_document = "document_text" in session
    chat_history = session.get("chat_history", [])
    filename = session.get("filename", "")
    return render_template("index.html",
                           has_document=has_document,
                           chat_history=chat_history,
                           filename=filename)


@main.route("/upload", methods=["POST"])
def upload():
    pdf_file = request.files.get("pdf")

    if not pdf_file or pdf_file.filename == "":
        return render_template("index.html", error="Please upload a PDF file.", has_document=False)

    if not pdf_file.filename.lower().endswith(".pdf"):
        return render_template("index.html", error="Only PDF files are supported.", has_document=False)

    try:
        document_text = extract_text_from_pdf(pdf_file)

        if not document_text:
            return render_template("index.html",
                                   error="Could not extract text from PDF. It may be scanned/image-based.",
                                   has_document=False)

        session["document_text"] = document_text
        session["chat_history"] = []
        session["filename"] = pdf_file.filename

        return render_template("index.html",
                               has_document=True,
                               chat_history=[],
                               filename=pdf_file.filename)

    except Exception as e:
        return render_template("index.html", error=f"An error occurred: {str(e)}", has_document=False)


@main.route("/chat", methods=["POST"])
def chat():
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
        chat_history = session.get("chat_history", [])
        chat_history.append({"role": "user", "content": question})

        response = get_response(session["document_text"], chat_history)

        chat_history.append({"role": "assistant", "content": response})
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


@main.route("/reset", methods=["POST"])
def reset():
    session.clear()
    return render_template("index.html", has_document=False, chat_history=[])