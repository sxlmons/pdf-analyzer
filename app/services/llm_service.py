import google.generativeai as genai

SYSTEM_PROMPT = """You are an advanced PhD-level specialist with expertise across multiple academic disciplines. 
Analyze documents thoroughly, cite specific sections when relevant, and provide clear, well-structured responses. 
Be precise but accessible. When summarizing or answering questions about a document, ground your response 
in the actual content provided. Use markdown formatting for better readability."""


def configure(api_key):
    """Initialize the Gemini client with the given API key."""
    genai.configure(api_key=api_key)


def build_prompt(document_text, conversation_history):
    """Build the full prompt string from document text and conversation history."""
    prompt = f"""{SYSTEM_PROMPT}

--- DOCUMENT CONTENT ---
{document_text}
--- END DOCUMENT ---

Below is the conversation so far. Continue naturally from here.

"""
    for msg in conversation_history:
        role = "User" if msg["role"] == "user" else "Assistant"
        prompt += f"{role}: {msg['content']}\n\n"

    prompt += "Assistant: "
    return prompt


def get_response(document_text, conversation_history):
    """Send document + conversation history to Gemini and return the response."""
    prompt = build_prompt(document_text, conversation_history)
    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt)
    return response.text