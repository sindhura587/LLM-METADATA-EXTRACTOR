
import logging
from pydantic import BaseModel, Field, field_validator



logger = logging.getLogger("request_models")

class RawTextRequest(BaseModel):

    raw_text: str = Field(
        min_length=10,
        max_length=5000,
        description="Raw text input for metadata extraction"
    )

    @field_validator("raw_text")
    @classmethod
    def validate_raw_text(cls, value: str):
        if not value.strip():
            logger.warning("Validation failed: raw_text cannot be empty")
            raise ValueError("raw_text cannot be empty")
        if len(value.split()) < 3:
            logger.warning("Validation failed: raw_text must contain meaningful content")
            raise ValueError(
                "raw_text must contain meaningful content"
            )
        return value.strip()
