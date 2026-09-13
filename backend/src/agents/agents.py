import time
import pymupdf as fitz
from typing import Optional
from backend.src.config.env_config import settings
from backend.src.config.llm_client import llm_client
from backend.src.schema.schemas import (
    RawParsedData,
    EnrichedContent,
    ThemeConfig,
    GeneratedPortfolio,
    FinalPortfolioPayload,
)
from backend.src.utils.logger import get_logger

logger = get_logger(__name__)

# ==========================================
# 1. INGESTION AGENT
# ==========================================
class IngestionAgent:
    @staticmethod
    def extract_text_from_pdf(pdf_bytes: bytes) -> str:
        byte_size = len(pdf_bytes)
        logger.debug(f"[IngestionAgent] Parsing PDF document ({byte_size} bytes)")
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            page_count = len(doc)
            text = "".join(page.get_text("text") + "\n" for page in doc).strip()
            logger.info(
                f"[IngestionAgent] PDF parsed successfully | Pages: {page_count} | "
                f"Extracted characters: {len(text)}"
            )
            if not text:
                logger.warning("[IngestionAgent] Extracted PDF text is completely empty.")
            elif len(text) < 50:
                logger.warning(f"[IngestionAgent] Extracted text is unusually short ({len(text)} chars)")
            return text
        except Exception as e:
            logger.error(f"[IngestionAgent] Failed to read PDF stream: {str(e)}", exc_info=True)
            raise

    @classmethod
    def run(cls, pdf_bytes: bytes) -> RawParsedData:
        logger.info("[IngestionAgent] Starting resume ingestion step")
        start_time = time.perf_counter()

        raw_text = cls.extract_text_from_pdf(pdf_bytes)
        if not raw_text:
            raise ValueError("Empty or unreadable PDF document.")

        try:
            result = llm_client.generate_structured_output(
                model=settings.ingestion_model,
                system_prompt=(
                    "You are an expert Data Ingestion Agent. Extract candidate profile data "
                    "from the resume text into the required structured schema accurately and concisely.\n"
                    "- Extract ONLY factual information present in the resume text.\n"
                    "- Do NOT invent, hallucinate, or duplicate work experiences, projects, or skills.\n"
                    "- Group bullet points by distinct jobs/companies rather than splitting each bullet into a separate experience.\n"
                    "- Keep entries clean, distinct, and directly derived from the input."
                ),
                user_prompt=f"Resume Text:\n\n{raw_text}",
                response_model=RawParsedData,
                max_tokens=settings.default_max_tokens,
            )
            elapsed = time.perf_counter() - start_time
            logger.info(
                f"[IngestionAgent] Completed ingestion in {elapsed:.2f}s | "
                f"Candidate: '{result.full_name}' | Headline: '{result.headline}' | "
                f"Skills: {len(result.skills)} | Projects: {len(result.projects)} | "
                f"Experience: {len(result.experience)}"
            )
            return result
        except Exception as e:
            elapsed = time.perf_counter() - start_time
            logger.error(
                f"[IngestionAgent] Step failed after {elapsed:.2f}s: {str(e)}",
                exc_info=True
            )
            raise


# ==========================================
# 2. STORYTELLER & COPYWRITING AGENT
# ==========================================
class StorytellerAgent:
    @classmethod
    def run(cls, parsed_data: RawParsedData, target_role: str = "Software Engineer") -> EnrichedContent:
        logger.info(
            f"[StorytellerAgent] Starting storytelling enhancement | "
            f"Candidate: '{parsed_data.full_name}' | Target Role: '{target_role}' | "
            f"Projects: {len(parsed_data.projects)} | Experience: {len(parsed_data.experience)}"
        )
        start_time = time.perf_counter()

        user_prompt = (
            f"Candidate Data:\n{parsed_data.model_dump_json(indent=2)}\n\n"
            f"Target Role Tone: {target_role}\n"
            "Task:\n"
            "1. Rewrite the bio into an engaging 2-3 sentence portfolio hook.\n"
            "2. Elevate project and experience bullets using STAR methodology (Action + Context + Quantified Impact).\n"
            "3. Ensure the tone is punchy, authentic, and modern."
        )

        try:
            result = llm_client.generate_structured_output(
                model=settings.storyteller_model,
                system_prompt="You are a master portfolio copywriter and technical storyteller.",
                user_prompt=user_prompt,
                response_model=EnrichedContent,
                temperature=0.4,
                max_tokens=settings.default_max_tokens,
            )
            elapsed = time.perf_counter() - start_time
            logger.info(
                f"[StorytellerAgent] Completed storytelling in {elapsed:.2f}s | "
                f"Bio characters: {len(result.storytelling_bio)} | "
                f"Enhanced Projects: {len(result.projects)} | "
                f"Enhanced Experience: {len(result.experience)}"
            )
            return result
        except Exception as e:
            elapsed = time.perf_counter() - start_time
            logger.error(
                f"[StorytellerAgent] Step failed after {elapsed:.2f}s: {str(e)}",
                exc_info=True
            )
            raise


# ==========================================
# 3. DESIGN & LAYOUT AGENT
# ==========================================
class DesignLayoutAgent:
    @classmethod
    def run(cls, enriched_data: EnrichedContent, user_theme_preference: Optional[str] = None) -> ThemeConfig:
        pref_str = user_theme_preference or "None specified"
        logger.info(
            f"[DesignLayoutAgent] Starting layout and styling selection | "
            f"Candidate Headline: '{enriched_data.headline}' | Theme Preference: '{pref_str}'"
        )
        start_time = time.perf_counter()

        user_pref_prompt = f"User preference: {user_theme_preference}" if user_theme_preference else "No specific preference."

        user_prompt = (
            f"Candidate Headline: {enriched_data.headline}\n"
            f"Skills: {', '.join(enriched_data.skills[:8])}\n"
            f"{user_pref_prompt}\n\n"
            "Select the best layout_style ('bento-grid', 'minimal-editorial', or 'developer-terminal'), "
            "palette ('slate-modern', 'cyber-dark', 'emerald-clean', 'minimal-mono'), "
            "font family, and prioritize section order."
        )

        try:
            result = llm_client.generate_structured_output(
                model=settings.design_model,
                system_prompt="You are a Creative Director and Design Systems Architect for modern web portfolios.",
                user_prompt=user_prompt,
                response_model=ThemeConfig,
                max_tokens=settings.default_max_tokens,
            )
            elapsed = time.perf_counter() - start_time
            logger.info(
                f"[DesignLayoutAgent] Completed design selection in {elapsed:.2f}s | "
                f"Layout: '{result.layout_style}' | Palette: '{result.palette}' | "
                f"Font: '{result.font_family}' | Section order: {result.section_order}"
            )
            return result
        except Exception as e:
            elapsed = time.perf_counter() - start_time
            logger.error(
                f"[DesignLayoutAgent] Step failed after {elapsed:.2f}s: {str(e)}",
                exc_info=True
            )
            raise


# ==========================================
# 4. PORTFOLIO GENERATOR AGENT (HTML & CSS)
# 4. PORTFOLIO GENERATOR AGENT (HTML with Tailwind CSS & DaisyUI)
# ==========================================
class PortfolioGeneratorAgent:
    @classmethod
    def run(cls, enriched_data: EnrichedContent, theme: ThemeConfig) -> GeneratedPortfolio:
        logger.info(
            f"[PortfolioGeneratorAgent] Starting HTML & CSS code generation | "
            f"[PortfolioGeneratorAgent] Starting HTML code generation with Tailwind CSS & DaisyUI | "
            f"Candidate: '{enriched_data.full_name}' | Layout: '{theme.layout_style}' | "
            f"Palette: '{theme.palette}' | Font: '{theme.font_family}'"
        )
        start_time = time.perf_counter()

        user_prompt = (
            f"Candidate Profile Data:\n{enriched_data.model_dump_json(indent=2)}\n\n"
            f"Theme Configuration:\n{theme.model_dump_json(indent=2)}\n\n"
            "Task:\n"
            "1. Generate complete, valid, semantic HTML5 code for the candidate's portfolio website:\n"
            f"   - Organize sections according to the requested section order: {theme.section_order}.\n"
            "   - Use modern semantic HTML5 tags (<header>, <nav>, <main>, <section id='...'>, <article>, <footer>) and ARIA attributes.\n"
            "   - Render all candidate information faithfully: candidate name, headline, storytelling bio, skills with badges/pills, "
            "projects (title, tagline, description, STAR impact bullets, tech stack, and links), and experience (role, company, duration, impact bullets).\n"
            "   - Do not use markdown code block backticks in the strings; provide clean raw markup.\n"
            "2. Generate modern, responsive CSS code:\n"
            f"   - Implement the selected layout style ('{theme.layout_style}', e.g., bento-grid, minimal-editorial, developer-terminal).\n"
            f"   - Apply the selected color palette ('{theme.palette}') with CSS variables and typography ('{theme.font_family}').\n"
            "   - Include complete responsive design rules using Flexbox, CSS Grid, and media queries for mobile, tablet, and desktop.\n"
            "   - Provide sleek styling for navigation, hero section, project cards, experience timeline/cards, skill badges, and contact elements.\n"
            "Generate a complete, self-contained, production-ready HTML5 portfolio document.\n"
            "CRITICAL REQUIREMENT: HTML and CSS must NOT be separate. All styling must be embedded directly within the HTML document using Tailwind CSS, DaisyUI, or shadcn/ui-inspired utility classes.\n\n"
            "1. Document Structure & Head Setup:\n"
            "   - Provide valid HTML5 starting with <!DOCTYPE html> and full <head> and <body> tags.\n"
            "   - In <head>, load the following CDNs:\n"
            "     * Tailwind CSS CDN: <script src=\"https://cdn.tailwindcss.com\"></script>\n"
            "     * DaisyUI CDN: <link href=\"https://cdn.jsdelivr.net/npm/daisyui@latest/dist/full.min.css\" rel=\"stylesheet\" type=\"text/css\" />\n"
            "     * Font Awesome / Icons: <link rel=\"stylesheet\" href=\"https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css\" />\n"
            f"     * Google Fonts matching '{theme.font_family}' (e.g. Inter, JetBrains Mono, Plus Jakarta Sans).\n"
            f"   - Add a Tailwind config script in <head> if needed to configure the '{theme.palette}' color scheme, typography, and dark mode.\n"
            "2. Component Styling & Utility Classes (within HTML tags):\n"
            "   - Use Tailwind CSS and DaisyUI utility classes directly on HTML elements (class=\"...\"):\n"
            "     * Navbar: Sticky or fixed with backdrop blur, brand logo/name, navigation links, and theme accent.\n"
            "     * Hero / Headline: High-impact typography, candidate name, subtitle, bio hook, call-to-action buttons (e.g. 'btn btn-primary', 'btn btn-outline'), and social icon links.\n"
            "     * Skills: Modern badges/pills (e.g. 'badge badge-lg gap-2 py-4 px-4 font-medium') with hover transitions.\n"
            "     * Experience: Modern timeline or cards (e.g. DaisyUI 'timeline' or structured Tailwind cards) showing role, company, duration, and bullet points.\n"
            "     * Projects: Responsive card grid (e.g. 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6') with project tags, descriptions, STAR metrics, and live/github link buttons.\n"
            "     * Contact & Footer: Sleek contact cards, mailto link, LinkedIn/GitHub links, and copyright footer.\n"
            f"   - Match the requested layout style ('{theme.layout_style}') and color palette ('{theme.palette}').\n"
            f"   - Follow the section order: {theme.section_order}.\n"
            "   - Fully responsive design out-of-the-box (mobile, tablet, desktop) using Tailwind responsive prefixes (sm:, md:, lg:, xl:).\n"
            "   - ARIA labels and semantic tags (<header>, <nav>, <main>, <section>, <article>, <footer>) for full accessibility.\n"
            "   - Do NOT use markdown code block backticks; provide the raw HTML markup directly in html_code.\n"
            "3. Return the result adhering to the GeneratedPortfolio schema."
        )

        try:
            result = llm_client.generate_structured_output(
                model=settings.generator_model,
                system_prompt=(
                    "You are a Senior Frontend Engineer and UI/UX Designer specializing in building "
                    "production-ready, modern, accessible, and responsive personal portfolio websites."
                    "production-ready, modern, accessible, and responsive personal portfolio websites "
                    "using Tailwind CSS, DaisyUI, and shadcn/ui design patterns directly within HTML."
                ),
                user_prompt=user_prompt,
                response_model=GeneratedPortfolio,
                temperature=0.3,
                max_tokens=settings.generator_max_tokens,
            )
            elapsed = time.perf_counter() - start_time
            logger.info(
                f"[PortfolioGeneratorAgent] Completed code generation in {elapsed:.2f}s | "
                f"HTML size: {len(result.html_code)} chars | CSS size: {len(result.css_code)} chars"
                f"HTML size: {len(result.html_code)} chars"
            )
            return result
        except Exception as e:
            elapsed = time.perf_counter() - start_time
            logger.error(
                f"[PortfolioGeneratorAgent] Step failed after {elapsed:.2f}s: {str(e)}",
                exc_info=True
            )
            raise


# ==========================================
# 5. REVIEWER & QA AGENT (FINAL OUTPUT)
# ==========================================
class ReviewerAgent:
    @classmethod
    def run(
        cls,
        enriched_data: EnrichedContent,
        theme: ThemeConfig,
        generated_portfolio: GeneratedPortfolio,
    ) -> FinalPortfolioPayload:
        logger.info(
            f"[ReviewerAgent] Starting QA audit of generated portfolio and SEO generation | "
            f"Candidate: '{enriched_data.full_name}' | HTML: {len(generated_portfolio.html_code)} chars | "
            f"CSS: {len(generated_portfolio.css_code)} chars"
            f"Candidate: '{enriched_data.full_name}' | HTML: {len(generated_portfolio.html_code)} chars"
        )
        start_time = time.perf_counter()

        user_prompt = (
            f"Candidate Enriched Data:\n{enriched_data.model_dump_json(indent=2)}\n\n"
            f"Theme Configuration:\n{theme.model_dump_json(indent=2)}\n\n"
            f"Generated HTML Code:\n{generated_portfolio.html_code}\n\n"
            f"Generated CSS Code:\n{generated_portfolio.css_code}\n\n"
            f"Generated HTML Code (Self-Contained with Tailwind CSS & DaisyUI):\n{generated_portfolio.html_code}\n\n"
            "Task:\n"
            "1. Audit the generated portfolio code:\n"
            "1. Audit the self-contained portfolio HTML code:\n"
            "   - Check HTML validity, properly closed tags, semantic structure, accessibility (contrast, ARIA, alt tags), and section order.\n"
            f"   - Check CSS for responsive layout adherence ('{theme.layout_style}'), color palette fidelity ('{theme.palette}'), and styling completeness.\n"
            "   - Verify that HTML and CSS are NOT separate: Tailwind CSS CDN, DaisyUI CDN, and Google Fonts must be loaded in <head>, and all styling must use utility classes directly within HTML tags.\n"
            f"   - Check responsive layout adherence ('{theme.layout_style}'), color palette fidelity ('{theme.palette}'), and styling completeness.\n"
            "   - Verify that all candidate projects, metrics, work experiences, skills, and narrative bio are accurately included without loss or hallucination.\n"
            "2. Fix and polish the portfolio code:\n"
            "   - Correct any syntax errors, layout bugs, responsive glitches, or awkward styling in html_code and css_code.\n"
            "2. Fix and polish the portfolio HTML:\n"
            "   - Correct any syntax errors, layout bugs, responsive glitches, broken classes, or awkward styling in html_code.\n"
            "   - Ensure the output is a single, self-contained, production-ready HTML document.\n"
            "3. Produce the final output:\n"
            "   - Output the verified, production-ready html_code and css_code.\n"
            "   - Output the verified, production-ready html_code.\n"
            "   - Include full candidate details (full_name, headline, bio, theme, skills, projects, experience).\n"
            "   - Generate 5-8 relevant technical SEO keywords.\n"
            "   - Provide concise review_notes summarizing the QA checks and verification results."
        )

        try:
            result = llm_client.generate_structured_output(
                model=settings.reviewer_model,
                system_prompt=(
                    "You are a Quality Assurance Specialist, Frontend Code Auditor, and Technical SEO Reviewer. "
                    "Your responsibility is to thoroughly check the generated portfolio HTML and CSS, correct any defects, "
                    "and output the final, verified portfolio payload."
                    "Your responsibility is to thoroughly check the self-contained portfolio HTML (using Tailwind CSS and DaisyUI), "
                    "correct any defects, and output the final, verified portfolio payload."
                ),
                user_prompt=user_prompt,
                response_model=FinalPortfolioPayload,
                max_tokens=settings.reviewer_max_tokens,
            )
            elapsed = time.perf_counter() - start_time
            logger.info(
                f"[ReviewerAgent] Completed portfolio audit in {elapsed:.2f}s | "
                f"Final HTML: {len(result.html_code)} chars | Final CSS: {len(result.css_code)} chars | "
                f"Final HTML: {len(result.html_code)} chars | "
                f"SEO keywords ({len(result.seo_keywords)}): {result.seo_keywords}"
            )
            return result
        except Exception as e:
            elapsed = time.perf_counter() - start_time
            logger.error(
                f"[ReviewerAgent] Step failed after {elapsed:.2f}s: {str(e)}",
                exc_info=True
            )
            raise