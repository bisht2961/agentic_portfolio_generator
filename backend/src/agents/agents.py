import time
import pymupdf as fitz
from typing import Optional
from src.config.env_config import settings
from src.config.llm_client import llm_client
from src.schema.schemas import (
    RawParsedData,
    EnrichedContent,
    ThemeConfig,
    GeneratedPortfolio,
    FinalPortfolioPayload,
)
from src.utils.logger import get_logger

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
                    "- IMPORTANT: Group all bullet points for the same company/job together under ONE ExperienceItem in its `impact_bullets` list. Never create a separate ExperienceItem for individual bullet points or responsibilities.\n"
                    "- Keep entries clean, distinct, concise, and directly derived from the input."
                ),
                user_prompt=f"Resume Text:\n\n{raw_text}",
                response_model=RawParsedData,
                max_tokens=settings.ingestion_max_tokens,
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
                max_tokens=settings.storyteller_max_tokens,
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
# 4. PORTFOLIO GENERATOR AGENT (HTML with Tailwind CSS & DaisyUI)
# ==========================================
class PortfolioGeneratorAgent:
    @classmethod
    def run(cls, enriched_data: EnrichedContent, theme: ThemeConfig) -> GeneratedPortfolio:
        logger.info(
            f"[PortfolioGeneratorAgent] Starting HTML code generation with Tailwind CSS & DaisyUI | "
            f"Candidate: '{enriched_data.full_name}' | Layout: '{theme.layout_style}' | "
            f"Palette: '{theme.palette}' | Font: '{theme.font_family}'"
        )
        start_time = time.perf_counter()
        num_projects = len(enriched_data.projects)
        project_grid_cols = (
            "grid-cols-1 max-w-2xl mx-auto" if num_projects == 1
            else "grid-cols-1 md:grid-cols-2" if num_projects == 2
            else "grid-cols-1 md:grid-cols-2 lg:grid-cols-3"
        )

        user_prompt = (
            f"Candidate Profile Data:\n{enriched_data.model_dump_json(indent=2)}\n\n"
            f"Theme Configuration:\n{theme.model_dump_json(indent=2)}\n\n"
            "Task:\n"
            "Generate a complete, self-contained, production-ready HTML5 portfolio document.\n"
            "CRITICAL REQUIREMENT: All styling must be embedded directly within the HTML document using Tailwind CSS and DaisyUI utility classes.\n\n"
            "1. Document Structure & Head Setup:\n"
            "   - Provide valid HTML5 starting with <!DOCTYPE html> and full <head> and <body> tags.\n"
            "   - In <head>, load the following CDNs:\n"
            "     * Tailwind CSS CDN: <script src=\"https://cdn.tailwindcss.com\"></script>\n"
            "     * DaisyUI CDN: <link href=\"https://cdn.jsdelivr.net/npm/daisyui@latest/dist/full.min.css\" rel=\"stylesheet\" type=\"text/css\" />\n"
            "     * Font Awesome / Icons: <link rel=\"stylesheet\" href=\"https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css\" />\n"
            f"     * Google Fonts matching '{theme.font_family}' (e.g. Inter, JetBrains Mono, Plus Jakarta Sans, Fira Code).\n"
            "   - Tailwind Configuration Script (STRICT PLACEMENT RULE):\n"
            f"     * If configuring the '{theme.palette}' color scheme, fonts, or dark mode, you MUST place tailwind.config strictly inside a <script> tag:\n"
            "       <script>\n"
            "         tailwind.config = {\n"
            "           darkMode: 'class',\n"
            "           theme: { ... }\n"
            "         };\n"
            "       </script>\n"
            "     * NEVER place tailwind.config inside a <style> tag or CSS block! Any <style> tag must contain ONLY valid CSS rules (e.g. custom keyframe animations, glow effects).\n\n"
            "2. Component & Layout Rules:\n"
            f"   - Section Order: Organize sections strictly according to: {theme.section_order}.\n"
            "   - Semantic Markup: Use modern semantic HTML5 tags (<header>, <nav>, <main>, <section id='...'>, <article>, <footer>) and ARIA attributes for accessibility.\n"
            "   - Navigation / Header: Sticky or fixed header with backdrop blur, candidate name/logo, navigation anchor links, and theme accent.\n"
            "   - Hero / Headline: High-impact typography, candidate name, subtitle, narrative bio hook, CTA buttons (e.g. 'btn btn-primary', 'btn btn-outline'), and social icon links.\n"
            "   - Skills Section: Modern badges/pills (e.g. 'badge badge-lg gap-2 py-4 px-4 font-medium') with hover transitions.\n"
            "   - Projects Section Grid Rules (STRICT COLUMN MATCHING RULE):\n"
            f"     * You MUST match the grid column counts to the actual number of projects ({num_projects} project(s)).\n"
            f"     * For {num_projects} project(s), use the class '{project_grid_cols}' (e.g., 'grid-cols-1 md:grid-cols-2' for 2 projects). NEVER use 'lg:grid-cols-3' when there are only 2 projects, so there are no awkward empty columns.\n"
            "     * Render all project details: title, tagline, description, STAR impact bullets, tech stack badges, and live demo / github source links.\n"
            "   - Experience Section & DaisyUI Timeline Rules (STRICT TIMELINE RULES):\n"
            "     * When using DaisyUI timeline ('timeline timeline-vertical ...'):\n"
            "       - The 'timeline-middle' element represents the icon/marker and MUST NOT have the 'timeline-box' class. 'timeline-box' is strictly reserved for 'timeline-start' and 'timeline-end' content containers.\n"
            "       - <hr/> tags MUST be included within each <li> to connect the timeline elements (e.g. <hr/> before timeline-middle and/or <hr/> after timeline-middle).\n"
            "       - Display role, company, duration, and STAR impact bullets clearly within the timeline boxes.\n"
            "   - Contact & Footer: Sleek contact cards, mailto link, LinkedIn/GitHub links, and copyright footer.\n\n"
            "3. Responsive & Quality Requirements:\n"
            f"   - Match the requested layout style ('{theme.layout_style}') and color palette ('{theme.palette}').\n"
            "   - Fully responsive design out-of-the-box using Tailwind responsive prefixes (sm:, md:, lg:, xl:).\n"
            "   - Do NOT use markdown code block backticks (no ```html); output the raw HTML markup directly in html_code.\n"
            "4. Return the result adhering to the GeneratedPortfolio schema."
        )

        try:
            result = llm_client.generate_structured_output(
                model=settings.generator_model,
                system_prompt=(
                    "You are a Senior Frontend Engineer and UI/UX Designer specializing in building "
                    "production-ready, modern, accessible, and responsive personal portfolio websites "
                    "using Tailwind CSS, DaisyUI, and modern design patterns directly within self-contained HTML."
                ),
                user_prompt=user_prompt,
                response_model=GeneratedPortfolio,
                temperature=0.3,
                max_tokens=settings.generator_max_tokens,
            )
            elapsed = time.perf_counter() - start_time
            logger.info(
                f"[PortfolioGeneratorAgent] Completed code generation in {elapsed:.2f}s | "
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
            f"Candidate: '{enriched_data.full_name}' | HTML: {len(generated_portfolio.html_code)} chars"
        )
        start_time = time.perf_counter()
        num_projects = len(enriched_data.projects)
        project_grid_cols = (
            "grid-cols-1 max-w-2xl mx-auto" if num_projects == 1
            else "grid-cols-1 md:grid-cols-2" if num_projects == 2
            else "grid-cols-1 md:grid-cols-2 lg:grid-cols-3"
        )

        user_prompt = (
            f"Candidate Enriched Data:\n{enriched_data.model_dump_json(indent=2)}\n\n"
            f"Theme Configuration:\n{theme.model_dump_json(indent=2)}\n\n"
            f"Generated HTML Code (Self-Contained with Tailwind CSS & DaisyUI):\n{generated_portfolio.html_code}\n\n"
            "Task:\n"
            "1. Audit the self-contained portfolio HTML code against all required standards:\n"
            "   - HTML Validity & CDNs: Verify valid HTML5 structure (<!DOCTYPE html>, <head>, <body>), and proper CDN links for Tailwind CSS, DaisyUI, Font Awesome, and Google Fonts.\n"
            "   - Tailwind Config Placement Rule: Verify that tailwind.config is placed strictly inside a <script> tag (<script>tailwind.config = { ... }</script>). If tailwind.config was incorrectly placed inside a <style> tag, move it into a <script> tag and remove it from <style>.\n"
            "   - DaisyUI Timeline Rules: If a DaisyUI timeline is used:\n"
            "     * 'timeline-middle' MUST NOT have the 'timeline-box' class. Remove 'timeline-box' from any 'timeline-middle' element.\n"
            "     * <hr/> tags MUST be included within each <li> to connect the timeline elements. If missing, insert them.\n"
            f"   - Project Grid Columns: Verify that the project grid column count matches the actual number of candidate projects ({num_projects} project(s)). For {num_projects} project(s), ensure '{project_grid_cols}' is used (e.g., 'grid-cols-1 md:grid-cols-2' for 2 projects, NOT 'lg:grid-cols-3').\n"
            f"   - Theme Fidelity: Check responsive layout adherence ('{theme.layout_style}'), color palette fidelity ('{theme.palette}'), and styling completeness.\n"
            "   - Content Completeness: Verify that all candidate projects, metrics, work experiences, skills, and narrative bio are accurately included without loss or hallucination.\n"
            "2. Fix and polish the portfolio HTML:\n"
            "   - Correct any syntax errors, layout bugs, responsive glitches, broken classes, or awkward styling in html_code.\n"
            "   - Ensure the output is a single, self-contained, production-ready HTML document without markdown backticks.\n"
            "3. Produce the final output:\n"
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
                    "Your responsibility is to thoroughly check the self-contained portfolio HTML (using Tailwind CSS and DaisyUI), "
                    "correct any defects (especially tailwind.config placement, DaisyUI timeline classes, and grid columns), "
                    "and output the final, verified portfolio payload."
                ),
                user_prompt=user_prompt,
                response_model=FinalPortfolioPayload,
                max_tokens=settings.reviewer_max_tokens,
            )
            elapsed = time.perf_counter() - start_time
            logger.info(
                f"[ReviewerAgent] Completed portfolio audit in {elapsed:.2f}s | "
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