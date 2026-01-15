# PDF Analyzer

A simple AI-powered document analysis tool. Upload a PDF and chat with it using Google's Gemini API.

## Features

- Upload PDF documents
- Ask questions about the content
- Continuous conversation with follow-up questions
- Markdown-rendered responses

## Setup

1. Clone the repo:
   ```bash
   git clone https://github.com/YOUR_USERNAME/pdf-analyzer.git
   cd pdf-analyzer
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your Gemini API key:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```
   Get a free API key at: https://makersuite.google.com/app/apikey

5. Run the app:
   ```bash
   python app.py
   ```

6. Open http://127.0.0.1:5000 in your browser

## Tech Stack

- Flask
- Google Gemini API
- pypdf
- marked.js (for markdown rendering)