import os
import google.generativeai as genai

SYSTEM_PROMPT = """You are an advanced PhD-level specialist with expertise across multiple academic disciplines. 
Analyze documents thoroughly, cite specific sections when relevant, and provide clear, well-structured responses. 
Be precise but accessible. When summarizing or answering questions about a document, ground your response 
in the actual content provided. Use markdown formatting for better readability."""


def configure(api_key):
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def get_response(document_text, conversation_history):
    messages = f"""{SYSTEM_PROMPT}

--- DOCUMENT CONTENT ---
{document_text}
--- END DOCUMENT ---

Below is the conversation so far. Continue naturally from here.

"""
    for msg in conversation_history:
        role = "User" if msg["role"] == "user" else "Assistant"
        messages += f"{role}: {msg['content']}\n\n"

    messages += "Assistant: "

    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(messages)
    return response.text