
import logging
from fastapi import APIRouter, HTTPException

from app.models.request_models import RawTextRequest
from app.services.gemini_service import extract_metadata

logger = logging.getLogger("extractor_route")

router = APIRouter()



@router.post("/extract-metadata")
async def extract_metadata_api(request: RawTextRequest):
    logger.info("/extract-metadata endpoint called")
    try:
        result = await extract_metadata(
            request.raw_text
        )
        logger.info("Metadata extraction successful")
        return {
            "status": "success",
            "data": result.model_dump()
        }
    except ValueError as e:
        logger.warning(f"ValueError in extraction: {e}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Internal server error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
