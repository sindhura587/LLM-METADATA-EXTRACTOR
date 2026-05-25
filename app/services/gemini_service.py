

import logging
import hashlib
from functools import lru_cache
from google import genai
from google.genai import errors

from app.core.config import GEMINI_API_KEY
from app.models.response_models import MetadataResponse
from app.prompts.extraction_prompt import SYSTEM_PROMPT


logger = logging.getLogger("gemini_service")

# Simple in-memory cache for response caching
_response_cache = {}

# Fallback chain — tried in order until one succeeds
GEMINI_MODELS = [
    "gemini-2.5-flash",       # Primary: latest, most capable
    "gemini-2.0-flash-001",   # Fallback 1: stable 2.0
    "gemini-2.0-flash-lite",  # Fallback 2: lightest
]
 
# If confidence_score < this threshold, escalate to stronger model
CONFIDENCE_THRESHOLD = 70
ESCALATION_MODEL = "gemini-2.5-pro"


client = genai.Client(
    api_key=GEMINI_API_KEY
)



async def call_gemini_model(model_name: str, raw_text: str, uuid: str):
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
        logger.debug(f"Gemini response: {response.text}", extra={"uuid": uuid})
        result = MetadataResponse.model_validate_json(response.text)
        result.model_used = model_name
        return result
    except errors.APIError as e:
        logger.error(f"Error calling Gemini model: {e}", extra={"uuid": uuid})
        raise



async def extract_metadata(raw_text: str) -> MetadataResponse:
    # Input fingerprinting: hash the raw_text
    uuid = hashlib.sha256(raw_text.encode("utf-8")).hexdigest()
    logger.info(f"Input fingerprint (uuid): {uuid}")

    # Response caching
    if uuid in _response_cache:
        logger.info("Cache hit for input", extra={"uuid": uuid})
        return _response_cache[uuid]
    
    errors_list = []
    for model_name in GEMINI_MODELS:
        try:
            result = await call_gemini_model(model_name, raw_text, uuid)
            
            # Escalation logic based on confidence score
            if result.confidence_score < CONFIDENCE_THRESHOLD:
                logger.info(f"Confidence {result.confidence_score} below threshold {CONFIDENCE_THRESHOLD}. Escalating to {ESCALATION_MODEL}...")
                try:
                    result = await call_gemini_model(ESCALATION_MODEL, raw_text, uuid)
                except Exception as escalation_error:
                    logger.warning(f"Escalation to {ESCALATION_MODEL} failed: {escalation_error}. Falling back to original result.")
            
            _response_cache[uuid] = result
            return result
        except Exception as e:
            logger.warning(f"Model {model_name} failed: {e}", extra={"uuid": uuid})
            errors_list.append(f"{model_name}: {str(e)}")

    logger.error(f"All models failed: {errors_list}", extra={"uuid": uuid})
    raise RuntimeError(f"All Gemini models failed. Errors: {'; '.join(errors_list)}")
