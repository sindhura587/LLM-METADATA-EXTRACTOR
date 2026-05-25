# LLM Metadata Extractor

## Key Technical Decisions

- **FastAPI** was chosen for its speed, async support, and automatic OpenAPI documentation.
- **Pydantic** is used for request/response validation to ensure strict data contracts and easy error handling.
- **Google Gemini LLM** is integrated for advanced metadata extraction, with fallback logic for reliability.
- **Model Transparency**: Each response includes the specific model identifier (e.g., `gemini-2.0-flash-001`) to provide clarity on which model in the fallback chain generated the result.
- **Input Fingerprinting & Caching**: Utilizes SHA-256 hashing for input fingerprinting and an in-memory cache to improve response times and reduce API costs for duplicate requests.
- **Logging** is configured project-wide for observability and debugging, using Python's standard logging module.
- **Docker** support is provided for easy deployment and environment consistency.
- **Environment Variables** are managed via `python-dotenv` for secure and flexible configuration.
- **Modular Structure**: The codebase is organized into `core`, `models`, `routes`, `services`, and `prompts` for maintainability and scalability.

## Features

- FastAPI REST API
- Gemini LLM Integration
- Pydantic Validation
- Structured JSON Output
- Gemini Fallback Retry Logic
- Model Transparency (Model version tracking)
- Input Fingerprinting & Caching
- Unit Tests
- Health Endpoint
- Asynchronous Processing

---

## API Endpoints

### POST `/extract-metadata`

Extracts structured metadata from a block of text using Gemini LLMs.

**Request Body:**
```json
{
  "raw_text": "Python is an interpreted, high-level, general-purpose programming language. Its design philosophy emphasizes code readability."
}
```

**Success Response:**
```json
{
  "status": "success",
  "data": {
    "confidence_score": 98,
    "model_used": "gemini-2.5-flash",
    "extracted_metadata": {
      "primary_subject": "Python Programming Language",
      "tags": ["Programming", "Python", "Software Development"],
      "technical_keywords": ["Interpreted", "High-level", "Readability"],
      "entities": ["Python Software Foundation", "Guido van Rossum"]
    }
  }
}
```

---

## Install

```bash
pip install -r requirements.txt
```

---

## Run Application

```bash
uvicorn app.main:app --reload
```

---

## Run Tests

```bash
pytest
```

---

## Swagger Docs

http://127.0.0.1:8000/docs
