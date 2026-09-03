import fitz  # PyMuPDF
from typing import Optional
from src.config.env_config import settings
from src.config.llm_client import llm_client
from src.schema.schemas import (
    RawParsedData,
    EnrichedContent,
    ThemeConfig,
    FinalPortfolioPayload,
)

# ==========================================
# 1. INGESTION AGENT
# ==========================================
class IngestionAgent:
    @staticmethod
    def extract_text_from_pdf(pdf_bytes: bytes) -> str:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text = "".join(page.get_text("text") + "\n" for page in doc)
        return text.strip()

    @classmethod
    def run(cls, pdf_bytes: bytes) -> RawParsedData:
        raw_text = cls.extract_text_from_pdf(pdf_bytes)
        if not raw_text:
            raise ValueError("Empty or unreadable PDF document.")

        return llm_client.generate_structured_output(
            model=settings.ingestion_model,
            system_prompt=(
                "You are an expert Data Ingestion Agent. Extract candidate profile data "
                "from the resume text into the required structured schema accurately."
            ),
            user_prompt=f"Resume Text:\n\n{raw_text}",
            response_model=RawParsedData,
        )


# ==========================================
# 2. STORYTELLER & COPYWRITING AGENT
# ==========================================
class StorytellerAgent:
    @classmethod
    def run(cls, parsed_data: RawParsedData, target_role: str = "Software Engineer") -> EnrichedContent:
        user_prompt = (
            f"Candidate Data:\n{parsed_data.model_dump_json(indent=2)}\n\n"
            f"Target Role Tone: {target_role}\n"
            "Task:\n"
            "1. Rewrite the bio into an engaging 2-3 sentence portfolio hook.\n"
            "2. Elevate project and experience bullets using STAR methodology (Action + Context + Quantified Impact).\n"
            "3. Ensure the tone is punchy, authentic, and modern."
        )

        return llm_client.generate_structured_output(
            model=settings.storyteller_model,
            system_prompt="You are a master portfolio copywriter and technical storyteller.",
            user_prompt=user_prompt,
            response_model=EnrichedContent,
            temperature=0.4,
        )


# ==========================================
# 3. DESIGN & LAYOUT AGENT
# ==========================================
class DesignLayoutAgent:
    @classmethod
    def run(cls, enriched_data: EnrichedContent, user_theme_preference: Optional[str] = None) -> ThemeConfig:
        user_pref_prompt = f"User preference: {user_theme_preference}" if user_theme_preference else "No specific preference."

        user_prompt = (
            f"Candidate Headline: {enriched_data.headline}\n"
            f"Skills: {', '.join(enriched_data.skills[:8])}\n"
            f"{user_pref_prompt}\n\n"
            "Select the best layout_style ('bento-grid', 'minimal-editorial', or 'developer-terminal'), "
            "palette ('slate-modern', 'cyber-dark', 'emerald-clean', 'minimal-mono'), "
            "font family, and prioritize section order."
        )

        return llm_client.generate_structured_output(
            model=settings.design_model,
            system_prompt="You are a Creative Director and Design Systems Architect for modern web portfolios.",
            user_prompt=user_prompt,
            response_model=ThemeConfig,
        )


# ==========================================
# 4. REVIEWER & LINTER AGENT
# ==========================================
class ReviewerAgent:
    @classmethod
    def run(cls, enriched_data: EnrichedContent, theme: ThemeConfig) -> FinalPortfolioPayload:
        user_prompt = (
            f"Enriched Data:\n{enriched_data.model_dump_json(indent=2)}\n\n"
            f"Theme Config:\n{theme.model_dump_json(indent=2)}\n\n"
            "Review the combined data. Fix any awkward phrasing, verify all arrays are populated, "
            "and generate 5-8 relevant technical SEO keywords."
        )

        return llm_client.generate_structured_output(
            model=settings.reviewer_model,
            system_prompt="You are a Quality Assurance and SEO reviewer for portfolio applications.",
            user_prompt=user_prompt,
            response_model=FinalPortfolioPayload,
        )