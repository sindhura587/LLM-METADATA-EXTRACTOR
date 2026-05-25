import os
import sys
import logging
import hashlib
from typing import List, Optional
from fastapi import FastAPI, APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator
from dotenv import load_dotenv
from google import genai
from google.genai import errors

# 1. CONFIGURATION & ENVIRONMENT
load_dotenv()
sys.dont_write_bytecode = True

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = os.getenv("LOG_FORMAT", "%(asctime)s - %(levelname)s - %(name)s - %(message)s")
logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger("metadata_extractor")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PRIMARY_MODEL = "gemini-2.5-flash"
FALLBACK_MODEL = "gemini-1.5-flash"

# 2. PROMPT DEFINITION
SYSTEM_PROMPT = """
You are a metadata extraction engine.

Extract:
- primary_subject
- tags
- technical_keywords
- entities
- confidence_score

Rules:
1. Return ONLY valid JSON
2. confidence_score must be between 0 and 100
3. technical_keywords should contain technical concepts only
4. tags should include general topics and categories
5. entities should include specific names of people, organizations, or locations
6. Do not add explanations
"""

# 3. MODELS
class RawTextRequest(BaseModel):
    raw_text: str = Field(..., min_length=10, description="The text to process")

class ExtractedMetadata(BaseModel):
    primary_subject: str = Field(min_length=2, max_length=200)
    tags: List[str] = Field(min_items=1, max_items=10)
    technical_keywords: List[str] = Field(min_items=1, max_items=10)
    entities: List[str] = Field(default_factory=list)

    @field_validator("tags", "technical_keywords", "entities")
    @classmethod
    def remove_empty_values(cls, values):
        cleaned = [v.strip() for v in values if v.strip()]
        if not cleaned:
            raise ValueError("List cannot contain empty values")
        return cleaned

class MetadataResponse(BaseModel):
    confidence_score: int = Field(ge=0, le=100)
    model_used: str = Field(default="")
    extracted_metadata: ExtractedMetadata

# 4. SERVICE LOGIC & CACHING
_response_cache = {}
client = genai.Client(api_key=GEMINI_API_KEY)

async def call_gemini_model(model_name: str, raw_text: str, uuid: str) -> MetadataResponse:
    logger.info(f"Calling Gemini model: {model_name}", extra={"uuid": uuid})
    try:
        response = await client.aio.models.generate_content(
            model=model_name,
            contents=f"{SYSTEM_PROMPT}\n\nINPUT:\n{raw_text}",
            config={
                "response_mime_type": "application/json",
                "response_schema": MetadataResponse,
                "temperature": 0.2
            }
        )
        result = MetadataResponse.model_validate_json(response.text)
        result.model_used = model_name
        return result
    except errors.APIError as e:
        logger.error(f"API Error ({model_name}): {e}", extra={"uuid": uuid})
        raise

async def extract_metadata_logic(raw_text: str) -> MetadataResponse:
    uuid = hashlib.sha256(raw_text.encode("utf-8")).hexdigest()
    
    if uuid in _response_cache:
        logger.info("Cache hit", extra={"uuid": uuid})
        return _response_cache[uuid]

    try:
        # Attempt Primary
        result = await call_gemini_model(PRIMARY_MODEL, raw_text, uuid)
        _response_cache[uuid] = result
        return result
    except Exception as primary_error:
        logger.warning(f"Primary failed: {primary_error}", extra={"uuid": uuid})
        try:
            # Attempt Fallback
            result = await call_gemini_model(FALLBACK_MODEL, raw_text, uuid)
            _response_cache[uuid] = result
            return result
        except Exception as fallback_error:
            logger.error("Both models failed", extra={"uuid": uuid})
            raise RuntimeError(f"Models failed. Primary: {primary_error} | Fallback: {fallback_error}")

# 5. FASTAPI APPLICATION
app = FastAPI(title="LLM Metadata Extractor")

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/extract-metadata")
async def extract_metadata_api(request: RawTextRequest):
    logger.info("Extraction requested")
    try:
        result = await extract_metadata_logic(request.raw_text)
        return {
            "status": "success",
            "data": result.model_dump()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)