
import logging
from pydantic import BaseModel, Field, field_validator
from typing import List



logger = logging.getLogger("response_models")

class ExtractedMetadata(BaseModel):

    primary_subject: str = Field(
        min_length=2,
        max_length=200
    )

    tags: List[str] = Field(
        min_items=1,
        max_items=10
    )

    technical_keywords: List[str] = Field(
        min_items=1,
        max_items=10
    )

    @field_validator("tags", "technical_keywords")
    @classmethod
    def remove_empty_values(cls, values):
        cleaned = [
            value.strip()
            for value in values
            if value.strip()
        ]
        if not cleaned:
            logger.warning("Validation failed: List cannot contain empty values")
            raise ValueError(
                "List cannot contain empty values"
            )
        return cleaned


class MetadataResponse(BaseModel):

    confidence_score: int = Field(
        ge=0,
        le=100,
        description="Confidence score from 0 to 100"
    )

    model_used: str = Field(
        default="",
        description="The specific Gemini model version that produced this result"
    )

    extracted_metadata: ExtractedMetadata
