import pytest

from pydantic import ValidationError

from app.models.request_models import RawTextRequest
from app.models.response_models import (
    ExtractedMetadata,
    MetadataResponse
)


def test_valid_request():

    request = RawTextRequest(
        raw_text="Apollo mission launched from Florida"
    )

    assert request.raw_text == (
        "Apollo mission launched from Florida"
    )


def test_empty_request():

    with pytest.raises(ValidationError):

        RawTextRequest(
            raw_text="   "
        )


def test_short_request():

    with pytest.raises(ValidationError):

        RawTextRequest(
            raw_text="Hi"
        )


def test_valid_response_model():

    metadata = MetadataResponse(
        confidence_score=95,
        extracted_metadata=ExtractedMetadata(
            primary_subject="Apollo-11",
            tags=["NASA", "Florida"],
            technical_keywords=["telemetry"]
        )
    )

    assert metadata.confidence_score == 95


def test_invalid_confidence_score():

    with pytest.raises(ValidationError):

        MetadataResponse(
            confidence_score=150,
            extracted_metadata=ExtractedMetadata(
                primary_subject="Apollo-11",
                tags=["NASA"],
                technical_keywords=["telemetry"]
            )
        )
