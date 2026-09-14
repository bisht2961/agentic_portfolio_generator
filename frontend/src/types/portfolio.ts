/**
 * TypeScript mirror of backend Pydantic schemas (src/schema/schemas.py)
 */

export interface ProjectItem {
  title: string;
  tagline: string;
  description: string;
  key_metrics_and_impact: string[];
  tech_stack: string[];
  github_url?: string | null;
  live_url?: string | null;
}

export interface ExperienceItem {
  role: string;
  company: string;
  duration: string;
  impact_bullets: string[];
}

export interface ThemeConfig {
  palette: string;
  font_family: string;
  layout_style: string;
  section_order: string[];
}

export interface FinalPortfolioPayload {
  full_name: string;
  headline: string;
  bio: string;
  theme: ThemeConfig;
  skills: string[];
  projects: ProjectItem[];
  experience: ExperienceItem[];
  seo_keywords: string[];
  html_code: string;
  css_code?: string | null;
  review_notes?: string | null;
}

export interface AgentStatusEvent {
  agent: string;
  message: string;
}

export interface LogEntry {
  id: string;
  timestamp: string;
  agent: string;
  message: string;
  status: 'pending' | 'running' | 'completed' | 'error';
}

export type PipelineStage = 
  | 'idle' 
  | 'uploading' 
  | 'ingestion' 
  | 'storyteller' 
  | 'design' 
  | 'generator' 
  | 'reviewer' 
  | 'completed' 
  | 'error';

