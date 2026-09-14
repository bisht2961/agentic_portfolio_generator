import React from 'react';
import { FolderGit2, ExternalLink, Sparkles, CheckCircle, Code } from 'lucide-react';
import { RetroCard } from '../common/RetroCard';
import { RetroBadge } from '../common/RetroBadge';
import { ProjectItem } from '../../types/portfolio';

const GithubIcon = ({ className = "w-3.5 h-3.5" }: { className?: string }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22" />
  </svg>
);

interface ProjectGridProps {
  projects: ProjectItem[];
}

export const ProjectGrid: React.FC<ProjectGridProps> = ({ projects }) => {
  return (
    <section className="p-6 sm:p-8 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-3">
        <div>
          <h2 className="font-mono font-bold text-lg text-retro-cyan uppercase tracking-wider flex items-center gap-2">
            <FolderGit2 className="w-5 h-5 text-retro-yellow" />
            ENGINEERING SHOWCASE (BENTO MATRIX)
          </h2>
          <p className="text-xs text-slate-400 font-mono">
            Featured architectures, production deployments & impact metrics
          </p>
        </div>
        <RetroBadge variant="cyan" size="sm">
          {projects.length} Verified Repositories
        </RetroBadge>
      </div>

      {/* Bento Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {projects.map((project, idx) => {
          return (
            <RetroCard
              key={idx}
              title={project.title}
              subtitle={project.tagline}
              icon={<Code className="w-4 h-4 text-retro-yellow" />}
              headerAction={
                <div className="flex items-center gap-1.5">
                  {project.live_url ? (
                    <a
                      href={project.live_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="p-1 text-slate-300 hover:text-retro-cyan"
                      title="Live Demo"
                    >
                      <ExternalLink className="w-3.5 h-3.5" />
                    </a>
                  ) : null}
                  {project.github_url ? (
                    <a
                      href={project.github_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="p-1 text-slate-300 hover:text-retro-cyan"
                      title="Source Code"
                    >
                      <GithubIcon className="w-3.5 h-3.5" />
                    </a>
                  ) : null}
                </div>
              }
              className="flex flex-col justify-between"
            >
              <div className="space-y-4">
                {/* Description */}
                <p className="font-mono text-xs text-slate-300 leading-relaxed">
                  {project.description}
                </p>

                {/* Key Metrics and Impact (STAR) */}
                {project.key_metrics_and_impact && project.key_metrics_and_impact.length > 0 && (
                  <div className="space-y-2 bg-black/40 p-3 rounded border border-slate-800">
                    <div className="flex items-center gap-1.5 text-[11px] font-mono font-bold text-retro-yellow uppercase">
                      <Sparkles className="w-3 h-3" />
                      Key Metrics & Impact:
                    </div>
                    <ul className="space-y-1.5 font-mono text-xs text-slate-300">
                      {project.key_metrics_and_impact.map((metric, mIdx) => (
                        <li key={mIdx} className="flex items-start gap-2">
                          <CheckCircle className="w-3.5 h-3.5 text-retro-green shrink-0 mt-0.5" />
                          <span className="leading-snug">{metric}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Tech Stack Chips */}
                {project.tech_stack && project.tech_stack.length > 0 && (
                  <div className="flex flex-wrap gap-1.5 pt-1">
                    {project.tech_stack.map((tech, tIdx) => (
                      <RetroBadge key={tIdx} variant="slate" size="sm">
                        {tech}
                      </RetroBadge>
                    ))}
                  </div>
                )}

                {/* Action Links */}
                <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-xs font-mono">
                  <span className="text-[10px] text-slate-500 uppercase">
                    Status: Production Ready
                  </span>
                  <div className="flex items-center gap-2">
                    <a
                      href={project.github_url || '#'}
                      className={`px-2 py-1 text-[11px] font-bold border transition-colors ${
                        project.github_url
                          ? 'border-slate-600 text-slate-200 hover:border-retro-cyan hover:text-retro-cyan'
                          : 'border-slate-800 text-slate-600 cursor-not-allowed'
                      }`}
                      onClick={(e) => !project.github_url && e.preventDefault()}
                    >
                      {project.github_url ? 'GitHub Repo' : 'Private Repo'}
                    </a>
                    <a
                      href={project.live_url || '#'}
                      className={`px-2 py-1 text-[11px] font-bold border transition-colors ${
                        project.live_url
                          ? 'border-retro-yellow text-retro-yellow hover:bg-retro-yellow hover:text-black'
                          : 'border-slate-800 text-slate-600 cursor-not-allowed'
                      }`}
                      onClick={(e) => !project.live_url && e.preventDefault()}
                    >
                      {project.live_url ? 'Live App' : 'Internal App'}
                    </a>
                  </div>
                </div>
              </div>
            </RetroCard>
          );
        })}
      </div>
    </section>
  );
};

