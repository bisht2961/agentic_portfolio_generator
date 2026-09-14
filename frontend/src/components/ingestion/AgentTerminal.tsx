import React, { useEffect, useRef } from 'react';
import { Terminal, Cpu, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';
import { RetroCard } from '../common/RetroCard';
import { usePortfolioStore } from '../../store/usePortfolioStore';

const PIPELINE_STEPS = [
  { id: 'ingestion', name: 'Ingestion' },
  { id: 'storyteller', name: 'Storyteller' },
  { id: 'design', name: 'Design' },
  { id: 'generator', name: 'Generator' },
  { id: 'reviewer', name: 'Reviewer' },
];

export const AgentTerminal: React.FC = () => {
  const { logs, status, activeAgent } = usePortfolioStore();
  const logContainerRef = useRef<HTMLDivElement>(null);

  // Auto scroll to bottom of terminal when new logs are received
  useEffect(() => {
    if (logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
    }
  }, [logs]);

  // Determine current active step index
  const getCurrentStepIndex = () => {
    switch (status) {
      case 'uploading':
        return 0;
      case 'ingestion':
        return 0;
      case 'storyteller':
        return 1;
      case 'design':
        return 2;
      case 'generator':
        return 3;
      case 'reviewer':
        return 4;
      case 'completed':
        return 5;
      default:
        return -1;
    }
  };

  const currentStepIdx = getCurrentStepIndex();

  return (
    <RetroCard
      title="AGENT SWARM TELEMETRY"
      subtitle="Real-time multi-agent execution feed"
      icon={<Terminal className="w-4 h-4 text-retro-green" />}
      headerAction={
        <div className="flex items-center gap-2">
          <span className="flex h-2 w-2 relative">
            <span
              className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${
                status === 'error'
                  ? 'bg-retro-magenta'
                  : status === 'completed'
                  ? 'bg-retro-green'
                  : status !== 'idle'
                  ? 'bg-retro-yellow'
                  : 'bg-slate-500'
              }`}
            />
            <span
              className={`relative inline-flex rounded-full h-2 w-2 ${
                status === 'error'
                  ? 'bg-retro-magenta'
                  : status === 'completed'
                  ? 'bg-retro-green'
                  : status !== 'idle'
                  ? 'bg-retro-yellow'
                  : 'bg-slate-500'
              }`}
            />
          </span>
          <span className="text-[11px] font-mono text-slate-300 uppercase">
            {activeAgent}
          </span>
        </div>
      }
      className="h-full flex flex-col"
    >
      <div className="flex flex-col h-full space-y-3">
        {/* Pipeline Step Progress Bar */}
        <div className="grid grid-cols-5 gap-1 p-1 bg-black/40 border border-slate-800 rounded">
          {PIPELINE_STEPS.map((step, idx) => {
            const isFinished = currentStepIdx > idx || status === 'completed';
            const isCurrent = currentStepIdx === idx && status !== 'completed';

            return (
              <div
                key={step.id}
                className={`py-1 px-1.5 text-center font-mono text-[10px] transition-all flex flex-col items-center justify-center border ${
                  isFinished
                    ? 'border-retro-green bg-emerald-950/40 text-retro-green font-bold'
                    : isCurrent
                    ? 'border-retro-yellow bg-yellow-950/40 text-retro-yellow font-bold animate-pulse'
                    : 'border-slate-800 text-slate-500 bg-slate-900/30'
                }`}
              >
                <div className="flex items-center gap-1">
                  {isFinished ? (
                    <CheckCircle2 className="w-2.5 h-2.5" />
                  ) : isCurrent ? (
                    <Loader2 className="w-2.5 h-2.5 animate-spin" />
                  ) : (
                    <span className="w-2.5 text-[9px]">{idx + 1}</span>
                  )}
                  <span className="truncate">{step.name}</span>
                </div>
              </div>
            );
          })}
        </div>

        {/* 8-Bit Terminal Screen with CRT Scanline Effect */}
        <div className="relative flex-1 min-h-[260px] max-h-[360px] bg-black/90 border border-retro-cyan/40 p-3 crt-scanlines rounded flex flex-col font-mono text-xs overflow-hidden">
          {/* Decorative Terminal Header */}
          <div className="flex items-center justify-between pb-2 mb-2 border-b border-slate-800 text-[10px] text-slate-400">
            <span className="text-retro-cyan flex items-center gap-1">
              <Cpu className="w-3 h-3" /> AGENT_DISPATCHER://SSE_STREAM
            </span>
            <span>LOGS: {logs.length}</span>
          </div>

          {/* Scrolling Log Messages */}
          <div
            ref={logContainerRef}
            className="flex-1 overflow-y-auto space-y-2 retro-scroll pr-1 text-slate-300"
          >
            {logs.length === 0 ? (
              <div className="text-slate-500 italic py-6 text-center">
                &gt; Awaiting resume PDF submission to start multi-agent pipeline...
              </div>
            ) : (
              logs.map((log) => {
                const isError = log.status === 'error';
                const isRunning = log.status === 'running';

                return (
                  <div
                    key={log.id}
                    className="leading-relaxed flex items-start gap-2 hover:bg-slate-900/40 px-1 rounded transition-colors"
                  >
                    <span className="text-slate-500 text-[10px] select-none shrink-0 pt-0.5">
                      [{log.timestamp}]
                    </span>
                    <span
                      className={`px-1 rounded text-[10px] uppercase font-bold shrink-0 ${
                        isError
                          ? 'bg-retro-magenta/20 text-retro-magenta border border-retro-magenta/40'
                          : log.agent.includes('Ingestion')
                          ? 'bg-cyan-950 text-retro-cyan border border-cyan-800'
                          : log.agent.includes('Story')
                          ? 'bg-purple-950 text-purple-300 border border-purple-800'
                          : log.agent.includes('Design')
                          ? 'bg-amber-950 text-amber-300 border border-amber-800'
                          : log.agent.includes('Generator')
                          ? 'bg-blue-950 text-blue-300 border border-blue-800'
                          : log.agent.includes('Reviewer')
                          ? 'bg-emerald-950 text-retro-green border border-emerald-800'
                          : 'bg-slate-800 text-slate-300'
                      }`}
                    >
                      {log.agent}
                    </span>
                    <span
                      className={`break-words flex-1 ${
                        isError
                          ? 'text-retro-magenta font-semibold'
                          : isRunning
                          ? 'text-retro-yellow'
                          : 'text-slate-200'
                      }`}
                    >
                      {log.message}
                      {isRunning && (
                        <span className="inline-block w-1.5 h-3 ml-1 bg-retro-yellow animate-pulse align-middle" />
                      )}
                    </span>
                  </div>
                );
              })
            )}

            {/* Blinking Cursor at bottom */}
            <div className="flex items-center gap-1 text-retro-green pt-1 select-none">
              <span>&gt;</span>
              <span className="inline-block w-2 h-3.5 bg-retro-green animate-pulse" />
            </div>
          </div>
        </div>
      </div>
    </RetroCard>
  );
};

