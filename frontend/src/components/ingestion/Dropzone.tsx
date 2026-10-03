import React, { useState, useRef } from 'react';
import { Upload, FileText, Sparkles, RefreshCw, X, Play } from 'lucide-react';
import { RetroCard } from '../common/RetroCard';
import { RetroButton } from '../common/RetroButton';
import { RetroBadge } from '../common/RetroBadge';
import { usePortfolioStore } from '../../store/usePortfolioStore';
import { useAgentStream } from '../../hooks/useAgentStream';

const COMMON_ROLES = [
  'Full Stack Developer',
  'Backend Engineer',
  'AI / ML Engineer',
  'Frontend Specialist',
  'Cloud / DevOps Engineer',
];

const THEME_OPTIONS = [
  { id: 'emerald-clean', label: 'Emerald Clean' },
  { id: 'slate-modern', label: 'Slate Modern' },
  { id: 'cyber-dark', label: 'Cyber Dark' },
  { id: 'minimal-mono', label: 'Minimal Mono' },
];

export const Dropzone: React.FC = () => {
  const {
    targetRole,
    setTargetRole,
    themePreference,
    setThemePreference,
    selectedFile,
    setSelectedFile,
    status,
    loadSampleData,
    resetPipeline,
  } = usePortfolioStore();

  const { startStream, cancelStream } = useAgentStream();
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const isBusy = status !== 'idle' && status !== 'completed' && status !== 'error';

  const handleFile = (file: File) => {
    if (file.type !== 'application/pdf' && !file.name.endsWith('.pdf')) {
      alert('Only PDF resumes are supported.');
      return;
    }
    setSelectedFile(file);
  };

  const onDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const onDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  return (
    <RetroCard
      title="RESUME INGESTION PROTOCOL"
      subtitle="PDF upload & pipeline configuration"
      icon={<Upload className="w-4 h-4" />}
    >
      <div className="space-y-4">
        {/* Drop Area */}
        <div
          onDragOver={onDragOver}
          onDragLeave={onDragLeave}
          onDrop={onDrop}
          onClick={() => !isBusy && fileInputRef.current?.click()}
          className={`border-2 border-dashed rounded p-6 text-center cursor-pointer transition-all duration-150 relative overflow-hidden ${
            isDragOver
              ? 'border-retro-yellow bg-retro-yellow/10 shadow-retro-yellow-sm'
              : selectedFile
              ? 'border-retro-green bg-emerald-100/60 dark:bg-emerald-950/20'
              : 'border-retro-border bg-retro-input-inactive/40 hover:border-retro-cyan hover:bg-retro-input/30'
          }`}
        >
          <input
            type="file"
            ref={fileInputRef}
            onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
            accept=".pdf,application/pdf"
            className="hidden"
            disabled={isBusy}
          />

          {selectedFile ? (
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3 text-left">
                <div className="p-2.5 bg-emerald-100 dark:bg-emerald-950/60 border border-retro-green rounded">
                  <FileText className="w-6 h-6 text-retro-green" />
                </div>
                <div>
                  <p className="font-mono font-bold text-retro-body text-sm truncate max-w-[200px] sm:max-w-xs">
                    {selectedFile.name}
                  </p>
                  <p className="text-xs text-retro-green font-mono">
                    READY ({(selectedFile.size / 1024).toFixed(1)} KB)
                  </p>
                </div>
              </div>
              {!isBusy && (
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setSelectedFile(null);
                  }}
                  className="p-1 hover:bg-retro-panel rounded border border-transparent hover:border-retro-border text-retro-muted hover:text-retro-body"
                >
                  <X className="w-4 h-4" />
                </button>
              )}
            </div>
          ) : (
            <div className="flex flex-col items-center gap-2">
              <div className="p-3 bg-retro-surface border border-retro-border rounded-full text-retro-cyan">
                <Upload className="w-6 h-6 animate-pulse" />
              </div>
              <p className="font-mono text-sm font-bold text-retro-body">
                DRAG & DROP RESUME PDF HERE
              </p>
              <p className="text-xs text-retro-muted font-mono">
                or click to browse from your filesystem (max 10MB)
              </p>
            </div>
          )}
        </div>

        {/* Target Role Field */}
        <div className="space-y-1.5">
          <label className="text-xs font-mono font-bold uppercase tracking-wider text-retro-cyan flex items-center gap-1.5">
            Target Job Title / Focus
          </label>
          <input
            type="text"
            value={targetRole}
            onChange={(e) => setTargetRole(e.target.value)}
            placeholder="e.g. Full Stack Developer, AI Engineer"
            disabled={isBusy}
            className="w-full bg-retro-input-inactive focus:bg-retro-input border border-retro-border focus:border-retro-cyan px-3 py-2 text-sm font-mono text-retro-body placeholder:text-retro-muted/60 focus:outline-none rounded-none transition-colors"
          />
          {/* Quick role tags */}
          <div className="flex flex-wrap gap-1.5 pt-1">
            {COMMON_ROLES.map((role) => (
              <button
                key={role}
                type="button"
                onClick={() => setTargetRole(role)}
                disabled={isBusy}
                className={`text-[10px] font-mono px-2 py-0.5 border transition-all ${
                  targetRole === role
                    ? 'border-retro-yellow text-retro-body bg-retro-yellow/30 font-bold'
                    : 'border-retro-border text-retro-muted hover:border-retro-cyan hover:text-retro-body bg-retro-input-inactive/40'
                }`}
              >
                {role}
              </button>
            ))}
          </div>
        </div>

        {/* Theme Preference */}
        <div className="space-y-1.5">
          <label className="text-xs font-mono font-bold uppercase tracking-wider text-retro-cyan">
            Visual Theme Strategy
          </label>
          <div className="grid grid-cols-2 gap-2">
            {THEME_OPTIONS.map((theme) => (
              <button
                key={theme.id}
                type="button"
                onClick={() => setThemePreference(theme.id)}
                disabled={isBusy}
                className={`text-xs font-mono py-1.5 px-2.5 text-left border flex items-center justify-between transition-all ${
                  themePreference === theme.id
                    ? 'border-retro-cyan text-retro-cyan bg-retro-input font-bold'
                    : 'border-retro-border text-retro-muted hover:border-retro-cyan bg-retro-input-inactive/40'
                }`}
              >
                <span>{theme.label}</span>
                {themePreference === theme.id && (
                  <span className="w-1.5 h-1.5 rounded-full bg-retro-cyan animate-ping" />
                )}
              </button>
            ))}
          </div>
        </div>

        {/* Action Controls */}
        <div className="pt-2 border-t border-retro-border flex flex-col sm:flex-row gap-2">
          {isBusy ? (
            <RetroButton
              variant="magenta"
              className="w-full"
              onClick={cancelStream}
            >
              <X className="w-4 h-4" />
              ABORT PIPELINE
            </RetroButton>
          ) : (
            <RetroButton
              variant="yellow"
              className="w-full"
              onClick={() => startStream()}
              disabled={!selectedFile}
            >
              <Play className="w-4 h-4 fill-current" />
              GENERATE PORTFOLIO
            </RetroButton>
          )}

          <div className="flex gap-2">
            <RetroButton
              variant="cyan"
              className="flex-1 whitespace-nowrap"
              onClick={loadSampleData}
              disabled={isBusy}
            >
              <Sparkles className="w-4 h-4" />
              LOAD DEMO
            </RetroButton>
            <button
              onClick={resetPipeline}
              disabled={isBusy}
              title="Reset state"
              className="px-3 border-2 border-retro-border text-retro-muted hover:text-retro-body hover:border-retro-cyan bg-retro-panel"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </RetroCard>
  );
};

