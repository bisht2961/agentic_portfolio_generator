from pydantic import BaseModel, Field
from typing import List, Optional

class ProjectItem(BaseModel):
    title: str = Field(description="Project name")
    tagline: str = Field(description="One-sentence hook or value proposition")
    description: str = Field(description="Concise overview or context")
    key_metrics_and_impact: List[str] = Field(
        default_factory=list, 
        description="STAR format impact bullets with metrics"
    )
    tech_stack: List[str] = Field(default_factory=list)
    github_url: Optional[str] = None
    live_url: Optional[str] = None

class ExperienceItem(BaseModel):
    role: str
    company: str
    duration: str
    impact_bullets: List[str] = Field(default_factory=list)

class RawParsedData(BaseModel):
    """Output from Ingestion Agent"""
    full_name: str
    headline: str
    raw_bio: str
    skills: List[str] = Field(default_factory=list)
    projects: List[ProjectItem] = Field(default_factory=list)
    experience: List[ExperienceItem] = Field(default_factory=list)

class EnrichedContent(BaseModel):
    """Output from Storyteller Agent"""
    full_name: str
    headline: str
    storytelling_bio: str = Field(description="Polished 2-3 sentence narrative bio")
    skills: List[str]
    projects: List[ProjectItem]
    experience: List[ExperienceItem]

class ThemeConfig(BaseModel):
    """Output from Design/Layout Agent"""
    palette: str = Field(description="e.g., slate-modern, cyber-dark, emerald-clean, minimal-mono")
    font_family: str = Field(description="e.g., Inter, JetBrains Mono, Plus Jakarta Sans")
    layout_style: str = Field(description="bento-grid, minimal-editorial, developer-terminal")
    section_order: List[str] = Field(
        default_factory=lambda: ["hero", "projects", "experience", "skills", "contact"]
    )

class GeneratedPortfolio(BaseModel):
    """Output from Portfolio Generator Agent"""
    html_code: str = Field(description="Complete, valid, semantic HTML5 markup for the portfolio website")
    css_code: str = Field(description="Modern, responsive CSS stylesheet matching the design theme, palette, and layout")

class FinalPortfolioPayload(BaseModel):
    """Final verified response from Reviewer Agent"""
    full_name: str
    headline: str
    bio: str
    theme: ThemeConfig
    skills: List[str]
    projects: List[ProjectItem]
    experience: List[ExperienceItem]
    seo_keywords: List[str]
    html_code: str = Field(description="Production-ready, valid, semantic HTML code for the portfolio")
    css_code: str = Field(description="Responsive, polished CSS styling matching the design theme and layout")
    review_notes: Optional[str] = Field(
        default=None,
        description="QA review audit feedback or validation notes"
    )