

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


PRIMARY_MODEL = "gemini-2.5-flash"
FALLBACK_MODEL = "gemini-1.5-flash"


client = genai.Client(
    api_key=GEMINI_API_KEY
)



async def call_gemini_model(model_name: str, raw_text: str, uuid: str):
    logger.info(f"Calling Gemini model: {model_name}", extra={"uuid": uuid})
    try:
        response = await client.aio.models.generate_content(
            model=model_name,
            contents=f"""
            {SYSTEM_PROMPT}

            INPUT:
            {raw_text}
            """,
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

    try:
        result = await call_gemini_model(
            PRIMARY_MODEL,
            raw_text,
            uuid
        )
        _response_cache[uuid] = result
        return result
    except Exception as primary_error:
        logger.warning(f"Primary model failed: {str(primary_error)}", extra={"uuid": uuid})
        try:
            result = await call_gemini_model(
                FALLBACK_MODEL,
                raw_text,
                uuid
            )
            _response_cache[uuid] = result
            return result
        except Exception as fallback_error:
            logger.error(
                f"Both Gemini models failed. Primary Error: {str(primary_error)} | Fallback Error: {str(fallback_error)}",
                extra={"uuid": uuid}
            )
            raise RuntimeError(
                f"Both Gemini models failed. "
                f"Primary Error: {str(primary_error)} | "
                f"Fallback Error: {str(fallback_error)}"
            )
