import React from 'react';
import { Mail, Terminal, Sparkles, Award } from 'lucide-react';
import { RetroBadge } from '../common/RetroBadge';
import { FinalPortfolioPayload } from '../../types/portfolio';

const LinkedinIcon = ({ className = "w-3.5 h-3.5" }: { className?: string }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z" />
    <rect x="2" y="9" width="4" height="12" />
    <circle cx="4" cy="4" r="2" />
  </svg>
);

const GithubIcon = ({ className = "w-3.5 h-3.5" }: { className?: string }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22" />
  </svg>
);

interface HeroSectionProps {
  portfolio: FinalPortfolioPayload;
}

export const HeroSection: React.FC<HeroSectionProps> = ({ portfolio }) => {
  return (
    <section className="relative p-6 sm:p-8 bg-retro-panel border-b-2 border-retro-cyan/40">
      {/* Background Matrix Accents */}
      <div className="absolute top-3 right-4 flex items-center gap-2 opacity-60">
        <RetroBadge variant="cyan" size="sm" icon={<Terminal className="w-3 h-3" />}>
          {portfolio.theme?.palette || 'emerald-clean'}
        </RetroBadge>
        <RetroBadge variant="yellow" size="sm">
          {portfolio.theme?.layout_style || 'minimal-editorial'}
        </RetroBadge>
      </div>

      <div className="max-w-4xl mx-auto space-y-5">
        {/* Pixel Headline & Title */}
        <div className="space-y-2">
          <div className="inline-flex items-center gap-2 px-2.5 py-1 bg-retro-surface border border-retro-cyan/50 text-[11px] font-mono text-retro-cyan uppercase tracking-widest">
            <Sparkles className="w-3 h-3 text-retro-yellow animate-spin" />
            Verified Portfolio Profile
          </div>

          <h1 className="font-pixel text-2xl sm:text-4xl text-retro-yellow text-shadow-neon-yellow tracking-wider leading-relaxed">
            {portfolio.full_name}
          </h1>

          <p className="font-mono text-lg sm:text-xl text-retro-cyan font-bold tracking-wide">
            {portfolio.headline}
          </p>
        </div>

        {/* Storytelling Bio */}
        <p className="font-mono text-sm sm:text-base text-slate-300 leading-relaxed border-l-2 border-retro-yellow pl-4 py-1 bg-black/20">
          {portfolio.bio}
        </p>

        {/* Skills Pills */}
        <div className="space-y-2 pt-2">
          <p className="text-[11px] font-mono font-bold uppercase tracking-wider text-slate-400">
            Engineered Capabilities & Tech Stack
          </p>
          <div className="flex flex-wrap gap-1.5">
            {portfolio.skills.map((skill, idx) => (
              <RetroBadge
                key={idx}
                variant={idx % 3 === 0 ? 'cyan' : idx % 3 === 1 ? 'yellow' : 'green'}
                size="sm"
              >
                {skill}
              </RetroBadge>
            ))}
          </div>
        </div>

        {/* Contact & External Links */}
        <div className="pt-3 flex flex-wrap items-center gap-3">
          <a
            href={`mailto:${portfolio.full_name.toLowerCase().replace(/\s+/g, '.')}@example.com`}
            className="px-3.5 py-2 bg-retro-yellow text-black font-mono font-bold text-xs uppercase tracking-wider border-2 border-black shadow-retro-yellow-sm hover:bg-retro-yellow-hover flex items-center gap-1.5 active:translate-x-0.5 active:translate-y-0.5"
          >
            <Mail className="w-3.5 h-3.5" />
            Contact Candidate
          </a>

          <a
            href="https://linkedin.com"
            target="_blank"
            rel="noopener noreferrer"
            className="px-3.5 py-2 bg-retro-surface text-retro-cyan font-mono font-bold text-xs uppercase tracking-wider border-2 border-retro-cyan hover:bg-retro-panel flex items-center gap-1.5 shadow-[2px_2px_0px_#000]"
          >
            <LinkedinIcon className="w-3.5 h-3.5" />
            LinkedIn
          </a>

          <a
            href="https://github.com"
            target="_blank"
            rel="noopener noreferrer"
            className="px-3.5 py-2 bg-retro-surface text-slate-200 font-mono font-bold text-xs uppercase tracking-wider border-2 border-slate-700 hover:border-slate-500 hover:text-white flex items-center gap-1.5 shadow-[2px_2px_0px_#000]"
          >
            <GithubIcon className="w-3.5 h-3.5" />
            GitHub
          </a>

          {portfolio.review_notes && (
            <div className="ml-auto hidden sm:flex items-center gap-1 text-[11px] font-mono text-retro-green bg-emerald-950/40 border border-emerald-800/60 px-2.5 py-1">
              <Award className="w-3.5 h-3.5" />
              <span>QA Certified</span>
            </div>
          )}
        </div>
      </div>
    </section>
  );
};

