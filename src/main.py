import sys
from pathlib import Path

# Ensure the project root directory is in sys.path when executed directly
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import json
import asyncio
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from dotenv import load_dotenv
from typing import Optional

from src.schema.schemas import FinalPortfolioPayload
from src.agents.agents import (
    IngestionAgent,
    StorytellerAgent,
    DesignLayoutAgent,
    ReviewerAgent
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

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "Agentic Portfolio Engine"}


# ---------------------------------------------------------
# Synchronous Single-Shot Endpoint
# ---------------------------------------------------------
@app.post("/api/generate", response_model=FinalPortfolioPayload)
async def generate_portfolio(
    file: UploadFile = File(...),
    target_role: Optional[str] = Form("Full Stack Developer"),
    theme_preference: Optional[str] = Form(None),
):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF resumes are supported.")

    pdf_bytes = await file.read()

    try:
        # Agent 1: Ingestion
        parsed_data = IngestionAgent.run(pdf_bytes)

        # Agent 2: Storytelling
        enriched_data = StorytellerAgent.run(parsed_data, target_role=target_role)

        # Agent 3: Design & Layout
        theme = DesignLayoutAgent.run(enriched_data, user_theme_preference=theme_preference)

        # Agent 4: Reviewer & SEO
        final_payload = ReviewerAgent.run(enriched_data, theme)

        return final_payload

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent workflow failed: {str(e)}")


# ---------------------------------------------------------
# Server-Sent Events (SSE) Streaming Endpoint
# ---------------------------------------------------------
@app.post("/api/generate-stream")
async def generate_portfolio_stream(
    file: UploadFile = File(...),
    target_role: Optional[str] = Form("Full Stack Developer"),
    theme_preference: Optional[str] = Form(None),
):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF resumes are supported.")

    pdf_bytes = await file.read()

    async def event_generator():
        try:
            # Step 1: Ingestion
            yield {
                "event": "agent_status",
                "data": json.dumps({"agent": "Ingestion Agent", "message": "Parsing resume PDF and extracting entities..."})
            }
            parsed_data = await asyncio.to_thread(IngestionAgent.run, pdf_bytes)

            # Step 2: Storytelling
            yield {
                "event": "agent_status",
                "data": json.dumps({"agent": "Storyteller Agent", "message": "Refining project STAR metrics and narrative bio..."})
            }
            enriched_data = await asyncio.to_thread(StorytellerAgent.run, parsed_data, target_role)

            # Step 3: Design & Layout
            yield {
                "event": "agent_status",
                "data": json.dumps({"agent": "Design Agent", "message": "Selecting UI theme, typography, and section hierarchy..."})
            }
            theme = await asyncio.to_thread(DesignLayoutAgent.run, enriched_data, theme_preference)

            # Step 4: Reviewer
            yield {
                "event": "agent_status",
                "data": json.dumps({"agent": "Reviewer Agent", "message": "Running QA checks and SEO metadata generation..."})
            }
            final_payload = await asyncio.to_thread(ReviewerAgent.run, enriched_data, theme)

            # Step 5: Final Result
            yield {
                "event": "complete",
                "data": final_payload.model_dump_json()
            }

        except Exception as e:
            yield {
                "event": "error",
                "data": json.dumps({"error": str(e)})
            }

    return EventSourceResponse(event_generator())


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)