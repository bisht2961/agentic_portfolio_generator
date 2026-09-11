import sys
from pathlib import Path

# Ensure the project root directory is in sys.path when executed directly
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import json
import time
import asyncio
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from dotenv import load_dotenv
from typing import Optional

from src.config.env_config import settings
from src.utils.logger import setup_logging, get_logger

# Initialize centralized logging
setup_logging(log_level=settings.log_level, log_file=settings.log_file)
logger = get_logger("src.main")

from src.schema.schemas import FinalPortfolioPayload
from src.agents.agents import (
    IngestionAgent,
    StorytellerAgent,
    DesignLayoutAgent,
    PortfolioGeneratorAgent,
    ReviewerAgent,
)

load_dotenv()

app = FastAPI(title="Agentic Portfolio Generator Backend", version="1.0.0")

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    logger.info("=" * 60)
    logger.info(f"Starting {settings.app_name} Backend v1.0.0")
    logger.info(f"Log Level: {settings.log_level} | Log File: {settings.log_file}")
    logger.info(f"Ingestion Model: {settings.ingestion_model}")
    logger.info(f"Storyteller Model: {settings.storyteller_model}")
    logger.info(f"Design Model: {settings.design_model}")
    logger.info(f"Generator Model: {settings.generator_model}")
    logger.info(f"Reviewer Model: {settings.reviewer_model}")
    logger.info(f"Reasoning Effort: {settings.reasoning_effort}")
    logger.info(f"Default Max Tokens: {settings.default_max_tokens}")
    logger.info("=" * 60)


@app.get("/health")
def health_check():
    logger.debug("Health check probe received")
    return {"status": "ok", "service": "Agentic Portfolio Engine"}


# ---------------------------------------------------------
# Synchronous Single-Shot Endpoint
# ---------------------------------------------------------
@app.post("/api/generate", response_model=FinalPortfolioPayload)
async def generate_portfolio(
    request: Request,
    file: UploadFile = File(...),
    target_role: Optional[str] = Form("Full Stack Developer"),
    theme_preference: Optional[str] = Form(None),
):
    client_ip = request.client.host if request.client else "unknown"
    logger.info(
        f"Incoming POST /api/generate from {client_ip} | File: '{file.filename}' | "
        f"ContentType: '{file.content_type}' | Target Role: '{target_role}' | "
        f"Theme Preference: '{theme_preference}'"
    )

    if file.content_type != "application/pdf":
        logger.warning(
            f"Rejected /api/generate request from {client_ip}: unsupported content-type '{file.content_type}'"
        )
        raise HTTPException(status_code=400, detail="Only PDF resumes are supported.")

    total_start_time = time.perf_counter()
    pdf_bytes = await file.read()
    logger.debug(f"Read {len(pdf_bytes)} bytes from uploaded PDF '{file.filename}'")

    try:
        # Agent 1: Ingestion
        t0 = time.perf_counter()
        logger.info("[Pipeline] Step 1/5: Ingestion Agent starting...")
        parsed_data = IngestionAgent.run(pdf_bytes)
        logger.info(f"[Pipeline] Step 1/5: Ingestion Agent finished in {time.perf_counter() - t0:.2f}s")

        # Agent 2: Storytelling
        t0 = time.perf_counter()
        logger.info(f"[Pipeline] Step 2/5: Storyteller Agent starting (target_role: '{target_role}')...")
        enriched_data = StorytellerAgent.run(parsed_data, target_role=target_role)
        logger.info(f"[Pipeline] Step 2/5: Storyteller Agent finished in {time.perf_counter() - t0:.2f}s")

        # Agent 3: Design & Layout
        t0 = time.perf_counter()
        logger.info(f"[Pipeline] Step 3/5: Design & Layout Agent starting (preference: '{theme_preference}')...")
        theme = DesignLayoutAgent.run(enriched_data, user_theme_preference=theme_preference)
        logger.info(f"[Pipeline] Step 3/5: Design & Layout Agent finished in {time.perf_counter() - t0:.2f}s")

        # Agent 4: Portfolio Generator (HTML & CSS)
        t0 = time.perf_counter()
        logger.info("[Pipeline] Step 4/5: Portfolio Generator Agent starting...")
        generated_portfolio = PortfolioGeneratorAgent.run(enriched_data, theme)
        logger.info(f"[Pipeline] Step 4/5: Portfolio Generator Agent finished in {time.perf_counter() - t0:.2f}s")

        # Agent 5: Reviewer & QA (Final Verified Portfolio)
        t0 = time.perf_counter()
        logger.info("[Pipeline] Step 5/5: Reviewer Agent starting QA audit...")
        final_payload = ReviewerAgent.run(enriched_data, theme, generated_portfolio)
        logger.info(f"[Pipeline] Step 5/5: Reviewer Agent finished in {time.perf_counter() - t0:.2f}s")

        total_elapsed = time.perf_counter() - total_start_time
        logger.info(
            f"POST /api/generate completed successfully in {total_elapsed:.2f}s for candidate '{final_payload.full_name}'"
        )
        return final_payload

    except Exception as e:
        total_elapsed = time.perf_counter() - total_start_time
        logger.error(
            f"POST /api/generate failed after {total_elapsed:.2f}s: {str(e)}",
            exc_info=True
        )
        raise HTTPException(status_code=500, detail=f"Agent workflow failed: {str(e)}")


# ---------------------------------------------------------
# Server-Sent Events (SSE) Streaming Endpoint
# ---------------------------------------------------------
@app.post("/api/generate-stream")
async def generate_portfolio_stream(
    request: Request,
    file: UploadFile = File(...),
    target_role: Optional[str] = Form("Full Stack Developer"),
    theme_preference: Optional[str] = Form(None),
):
    client_ip = request.client.host if request.client else "unknown"
    logger.info(
        f"Incoming POST /api/generate-stream from {client_ip} | File: '{file.filename}' | "
        f"ContentType: '{file.content_type}' | Target Role: '{target_role}' | "
        f"Theme Preference: '{theme_preference}'"
    )

    if file.content_type != "application/pdf":
        logger.warning(
            f"Rejected /api/generate-stream request from {client_ip}: unsupported content-type '{file.content_type}'"
        )
        raise HTTPException(status_code=400, detail="Only PDF resumes are supported.")

    pdf_bytes = await file.read()
    logger.debug(f"Read {len(pdf_bytes)} bytes from uploaded PDF '{file.filename}'")

    async def event_generator():
        stream_start_time = time.perf_counter()
        try:
            # Step 1: Ingestion
            logger.info("[Stream Pipeline] Step 1/5: Ingestion Agent starting...")
            yield {
                "event": "agent_status",
                "data": json.dumps({"agent": "Ingestion Agent", "message": "Parsing resume PDF and extracting entities..."})
            }
            t0 = time.perf_counter()
            parsed_data = await asyncio.to_thread(IngestionAgent.run, pdf_bytes)
            logger.info(f"[Stream Pipeline] Step 1/5: Ingestion Agent finished in {time.perf_counter() - t0:.2f}s")

            # Step 2: Storytelling
            logger.info(f"[Stream Pipeline] Step 2/5: Storyteller Agent starting (target_role: '{target_role}')...")
            yield {
                "event": "agent_status",
                "data": json.dumps({"agent": "Storyteller Agent", "message": "Refining project STAR metrics and narrative bio..."})
            }
            t0 = time.perf_counter()
            enriched_data = await asyncio.to_thread(StorytellerAgent.run, parsed_data, target_role)
            logger.info(f"[Stream Pipeline] Step 2/5: Storyteller Agent finished in {time.perf_counter() - t0:.2f}s")

            # Step 3: Design & Layout
            logger.info(f"[Stream Pipeline] Step 3/5: Design & Layout Agent starting (preference: '{theme_preference}')...")
            yield {
                "event": "agent_status",
                "data": json.dumps({"agent": "Design Agent", "message": "Selecting UI theme, typography, and section hierarchy..."})
            }
            t0 = time.perf_counter()
            theme = await asyncio.to_thread(DesignLayoutAgent.run, enriched_data, theme_preference)
            logger.info(f"[Stream Pipeline] Step 3/5: Design & Layout Agent finished in {time.perf_counter() - t0:.2f}s")

            # Step 4: Portfolio Generator (HTML & CSS)
            logger.info("[Stream Pipeline] Step 4/5: Portfolio Generator Agent starting...")
            yield {
                "event": "agent_status",
                "data": json.dumps({"agent": "Portfolio Generator Agent", "message": "Generating responsive HTML and CSS portfolio code..."})
            }
            t0 = time.perf_counter()
            generated_portfolio = await asyncio.to_thread(PortfolioGeneratorAgent.run, enriched_data, theme)
            logger.info(f"[Stream Pipeline] Step 4/5: Portfolio Generator Agent finished in {time.perf_counter() - t0:.2f}s")

            # Step 5: Reviewer & QA (Final Verified Portfolio)
            logger.info("[Stream Pipeline] Step 5/5: Reviewer Agent starting QA audit...")
            yield {
                "event": "agent_status",
                "data": json.dumps({"agent": "Reviewer Agent", "message": "Auditing portfolio code, accessibility, styling, and SEO..."})
            }
            t0 = time.perf_counter()
            final_payload = await asyncio.to_thread(ReviewerAgent.run, enriched_data, theme, generated_portfolio)
            logger.info(f"[Stream Pipeline] Step 5/5: Reviewer Agent finished in {time.perf_counter() - t0:.2f}s")

            # Step 6: Final Result
            total_elapsed = time.perf_counter() - stream_start_time
            logger.info(
                f"[Stream Pipeline] Finished all steps in {total_elapsed:.2f}s. Sending final payload for '{final_payload.full_name}'"
            )
            yield {
                "event": "complete",
                "data": final_payload.model_dump_json()
            }

        except Exception as e:
            total_elapsed = time.perf_counter() - stream_start_time
            logger.error(
                f"[Stream Pipeline] Stream generation failed after {total_elapsed:.2f}s: {str(e)}",
                exc_info=True
            )
            yield {
                "event": "error",
                "data": json.dumps({"error": str(e)})
            }

    return EventSourceResponse(event_generator())


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)