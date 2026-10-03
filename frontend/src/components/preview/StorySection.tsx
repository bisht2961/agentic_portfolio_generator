import React from 'react';
import { Target, Zap, ShieldCheck, Briefcase, ArrowRight, TrendingUp } from 'lucide-react';
import { RetroCard } from '../common/RetroCard';
import { RetroBadge } from '../common/RetroBadge';
import { ExperienceItem } from '../../types/portfolio';

interface StorySectionProps {
  experience: ExperienceItem[];
}

export const StorySection: React.FC<StorySectionProps> = ({ experience }) => {
  // Helper to extract or structure outcome -> obstacle -> solution from bullets
  const parseBulletToStory = (bullet: string) => {
    // If bullet contains metric percentages or multipliers, highlight as outcome
    const metricMatch = bullet.match(/\b(\d+%(?:\+)?|\d+x|<2s|\d+,\d+\+?)\b/i);
    const metric = metricMatch ? metricMatch[0] : null;

    return {
      text: bullet,
      metric,
    };
  };

  return (
    <section className="p-6 sm:p-8 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-retro-border pb-3">
        <div>
          <h2 className="font-mono font-bold text-lg text-retro-cyan uppercase tracking-wider flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-retro-yellow" />
            NARRATIVE IMPACT ENGINE (STAR METHODOLOGY)
          </h2>
          <p className="text-xs text-retro-muted font-mono">
            Outcome &rarr; Obstacle &rarr; Solution structured career milestones
          </p>
        </div>
        <RetroBadge variant="yellow" size="sm">
          {experience.length} Professional Tenures
        </RetroBadge>
      </div>

      <div className="space-y-6">
        {experience.map((exp, expIdx) => (
          <RetroCard
            key={expIdx}
            title={`${exp.role} @ ${exp.company}`}
            subtitle={exp.duration}
            icon={<Briefcase className="w-4 h-4 text-retro-cyan" />}
          >
            <div className="space-y-4">
              {/* Timeline Header Badge */}
              <div className="flex items-center gap-2 text-xs font-mono text-retro-muted border-b border-retro-border pb-2">
                <span className="text-retro-yellow font-bold">ORGANIZATION:</span>
                <span className="text-retro-body font-semibold">{exp.company}</span>
                <span className="text-retro-muted">|</span>
                <span className="text-retro-cyan font-bold">DURATION:</span>
                <span className="text-retro-body">{exp.duration}</span>
              </div>

              {/* Grid of Outcome -> Obstacle -> Solution Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {exp.impact_bullets.map((bullet, bIdx) => {
                  const story = parseBulletToStory(bullet);

                  return (
                    <div
                      key={bIdx}
                      className="bg-retro-panel border border-retro-border hover:border-retro-cyan/60 p-3 rounded transition-all flex flex-col justify-between group"
                    >
                      <div className="space-y-2">
                        {/* Outcome Tag */}
                        <div className="flex items-center justify-between">
                          <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-retro-yellow flex items-center gap-1">
                            <Target className="w-3 h-3" /> OUTCOME
                          </span>
                          {story.metric && (
                            <span className="px-1.5 py-0.5 bg-amber-100 text-[#CA8A04] border border-[#EAB308] dark:bg-yellow-950/80 dark:border-retro-yellow dark:text-retro-yellow font-mono text-[10px] font-bold">
                              {story.metric} IMPACT
                            </span>
                          )}
                        </div>

                        {/* Story Content */}
                        <p className="font-mono text-xs text-retro-body leading-relaxed">
                          {bullet}
                        </p>
                      </div>

                      {/* Technical Execution Vector */}
                      <div className="pt-2 mt-2 border-t border-retro-border/80 flex items-center gap-2 text-[10px] font-mono text-retro-muted">
                        <span className="text-retro-cyan flex items-center gap-0.5">
                          <Zap className="w-3 h-3" /> Solution
                        </span>
                        <ArrowRight className="w-2.5 h-2.5 text-retro-muted" />
                        <span className="text-retro-green flex items-center gap-0.5">
                          <ShieldCheck className="w-3 h-3" /> Verified
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </RetroCard>
        ))}
      </div>
    </section>
  );
};

