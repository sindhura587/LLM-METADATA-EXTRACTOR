
import logging
from fastapi import FastAPI
from app.routes.extractor import router

logger = logging.getLogger("main")

app = FastAPI(
    title="LLM Metadata Extractor",
    version="1.0.0"
)

app.include_router(router)

@app.on_event("startup")
async def startup_event():
    logger.info("Application startup: LLM Metadata Extractor is starting.")


@app.get("/health")
async def health():
    logger.debug("Health check endpoint called.")
    try:
        return {"status": "healthy"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "error", "detail": str(e)}
