import fitz  # PyMuPDF
import os
from openai import OpenAI
from schemas import (
    RawParsedData,
    EnrichedContent,
    ThemeConfig,
    FinalPortfolioPayload
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
DEFAULT_MODEL = "gpt-4o-mini"

# ==========================================
# 1. INGESTION AGENT
# ==========================================
class IngestionAgent:
    """Extracts raw text from PDF and structures it into RawParsedData."""
    
    @staticmethod
    def extract_text_from_pdf(pdf_bytes: bytes) -> str:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text("text") + "\n"
        return text.strip()

    @classmethod
    def run(cls, pdf_bytes: bytes) -> RawParsedData:
        raw_text = cls.extract_text_from_pdf(pdf_bytes)
        if not raw_text:
            raise ValueError("Empty or unreadable PDF document.")

        completion = client.beta.chat.completions.parse(
            model=DEFAULT_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert Data Ingestion Agent. Extract candidate profile data "
                        "from the resume text into the required structured schema accurately."
                    ),
                },
                {"role": "user", "content": f"Resume Text:\n\n{raw_text}"},
            ],
            response_format=RawParsedData,
        )
        return completion.choices[0].message.parsed


# ==========================================
# 2. STORYTELLER & COPYWRITING AGENT
# ==========================================
class StorytellerAgent:
    """Refines raw descriptions, synthesizes STAR metrics, and crafts punchy bios."""
    
    @classmethod
    def run(cls, parsed_data: RawParsedData, target_role: str = "Software Engineer") -> EnrichedContent:
        prompt = (
            f"Candidate Data:\n{parsed_data.model_dump_json(indent=2)}\n\n"
            f"Target Role Tone: {target_role}\n"
            "Task:\n"
            "1. Rewrite the bio into an engaging 2-3 sentence portfolio hook.\n"
            "2. Elevate project and experience bullets using STAR methodology (Action + Context + Quantified Impact).\n"
            "3. Ensure the tone is punchy, authentic, and modern."
        )

        completion = client.beta.chat.completions.parse(
            model=DEFAULT_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a master portfolio copywriter and technical storyteller.",
                },
                {"role": "user", "content": prompt},
            ],
            response_format=EnrichedContent,
        )
        return completion.choices[0].message.parsed


# ==========================================
# 3. DESIGN & LAYOUT AGENT
# ==========================================
class DesignLayoutAgent:
    """Determines section ordering, UI themes, and typography based on candidate profile."""
    
    @classmethod
    def run(cls, enriched_data: EnrichedContent, user_theme_preference: Optional[str] = None) -> ThemeConfig:
        user_pref_prompt = f"User preference: {user_theme_preference}" if user_theme_preference else "No specific preference."
        
        prompt = (
            f"Candidate Headline: {enriched_data.headline}\n"
            f"Skills: {', '.join(enriched_data.skills[:8])}\n"
            f"{user_pref_prompt}\n\n"
            "Select the best layout_style ('bento-grid', 'minimal-editorial', or 'developer-terminal'), "
            "palette ('slate-modern', 'cyber-dark', 'emerald-clean', 'minimal-mono'), "
            "font family, and prioritize section order (e.g. projects first for builders/juniors, experience first for leaders)."
        )

        completion = client.beta.chat.completions.parse(
            model=DEFAULT_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a Creative Director and Design Systems Architect for modern web portfolios.",
                },
                {"role": "user", "content": prompt},
            ],
            response_format=ThemeConfig,
        )
        return completion.choices[0].message.parsed


# ==========================================
# 4. REVIEWER & LINTER AGENT
# ==========================================
class ReviewerAgent:
    """Performs final schema validation, generates SEO metadata, and ensures clean output."""
    
    @classmethod
    def run(cls, enriched_data: EnrichedContent, theme: ThemeConfig) -> FinalPortfolioPayload:
        prompt = (
            f"Enriched Data:\n{enriched_data.model_dump_json(indent=2)}\n\n"
            f"Theme Config:\n{theme.model_dump_json(indent=2)}\n\n"
            "Review the combined data. Fix any awkward phrasing, verify all arrays are populated, "
            "and generate 5-8 relevant technical SEO keywords."
        )

        completion = client.beta.chat.completions.parse(
            model=DEFAULT_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a Quality Assurance and SEO reviewer for portfolio applications.",
                },
                {"role": "user", "content": prompt},
            ],
            response_format=FinalPortfolioPayload,
        )
        return completion.choices[0].message.parsed