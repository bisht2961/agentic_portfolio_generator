import React from 'react';
import { Terminal, Sparkles, Cpu, Layers } from 'lucide-react';
import { Dropzone } from './components/ingestion/Dropzone';
import { AgentTerminal } from './components/ingestion/AgentTerminal';
import { Canvas } from './components/preview/Canvas';
import { RetroBadge } from './components/common/RetroBadge';
import { ThemeToggle } from './components/common/ThemeToggle';
import { usePortfolioStore } from './store/usePortfolioStore';

export const App: React.FC = () => {
  const { status, portfolio } = usePortfolioStore();

  return (
    <div className="min-h-screen flex flex-col bg-retro-bg text-retro-body selection:bg-retro-cyan selection:text-black">
      {/* 8-Bit Cyber Arcade Header */}
      <header className="border-b-2 border-retro-cyan bg-retro-surface sticky top-0 z-40 shadow-hard-dark">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-3 flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            {/* Retro Arcade Icon Badge */}
            <div className="w-9 h-9 bg-retro-yellow border-2 border-retro-border flex items-center justify-center shadow-retro-yellow-sm">
              <Terminal className="w-5 h-5 text-black" />
            </div>
            <div>
              <h1 className="font-pixel text-xs sm:text-sm text-retro-heading tracking-wider flex items-center gap-2">
                AGENTIC PORTFOLIO GENERATOR
                <span className="text-[10px] px-1.5 py-0.2 bg-retro-cyan text-white dark:text-black font-mono font-bold">
                  8-BIT
                </span>
              </h1>
              <p className="font-mono text-[11px] text-retro-muted">
                Autonomous multi-agent resume-to-portfolio synthesizer
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 sm:gap-3">
            <ThemeToggle />

            <RetroBadge
              variant={status === 'completed' ? 'green' : status === 'error' ? 'magenta' : 'yellow'}
              size="sm"
              icon={<Cpu className="w-3 h-3" />}
            >
              PIPELINE: {status.toUpperCase()}
            </RetroBadge>

            {portfolio && (
              <div className="hidden sm:flex items-center gap-1.5 text-xs font-mono text-retro-muted bg-retro-panel/70 px-2.5 py-1 border border-retro-border">
                <Sparkles className="w-3.5 h-3.5 text-retro-cyan" />
                <span className="text-retro-body font-bold">{portfolio.full_name}</span>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Main App Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 py-6 space-y-6">
        {/* Ingestion & Agent Swarm Telemetry Section */}
        <section className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* Left: Resume Uploader & Strategy Options */}
          <div className="lg:col-span-5 w-full">
            <Dropzone />
          </div>

          {/* Right: 8-bit Animated Telemetry Terminal */}
          <div className="lg:col-span-7 w-full">
            <AgentTerminal />
          </div>
        </section>

        {/* Live Reactive Portfolio Canvas Wrapper */}
        <section className="w-full pt-2">
          <div className="flex items-center justify-between pb-3">
            <h2 className="font-pixel text-xs sm:text-sm text-retro-heading flex items-center gap-2">
              <Layers className="w-4 h-4 text-retro-yellow" />
              LIVE REACTIVE CANVAS PREVIEW
            </h2>
            <div className="text-[11px] font-mono text-retro-muted">
              SYNTHESIS ENGINE READY
            </div>
          </div>
          <Canvas />
        </section>
      </main>

      {/* Cyberpunk Footer */}
      <footer className="border-t-2 border-retro-border bg-retro-surface py-4 mt-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 flex flex-col sm:flex-row items-center justify-between gap-2 text-xs font-mono text-retro-muted">
          <div>
            &copy; 2026 Agentic Portfolio Generator • 5-Agent Autonomous Swarm (FastAPI + React + SSE)
          </div>
          <div className="flex items-center gap-3">
            <span className="hover:text-retro-cyan transition-colors cursor-default">
              INGESTION &rarr; STORYTELLER &rarr; DESIGN &rarr; GENERATOR &rarr; REVIEWER
            </span>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default App;

