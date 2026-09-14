import React, { useState } from 'react';
import {
  Monitor,
  Smartphone,
  Tablet,
  Download,
  Copy,
  Check,
  ExternalLink,
  Eye,
  Code2,
  Sparkles,
  Layers,
} from 'lucide-react';
import { RetroButton } from '../common/RetroButton';
import { RetroBadge } from '../common/RetroBadge';
import { HeroSection } from './HeroSection';
import { StorySection } from './StorySection';
import { ProjectGrid } from './ProjectGrid';
import { usePortfolioStore } from '../../store/usePortfolioStore';

export const Canvas: React.FC = () => {
  const { portfolio, viewMode, setViewMode } = usePortfolioStore();
  const [deviceWidth, setDeviceWidth] = useState<'desktop' | 'tablet' | 'mobile'>('desktop');
  const [copied, setCopied] = useState(false);

  if (!portfolio) {
    return (
      <div className="border-2 border-slate-800 bg-retro-surface p-12 text-center rounded-sm space-y-4">
        <div className="w-12 h-12 mx-auto bg-retro-panel border border-slate-700 flex items-center justify-center text-slate-500">
          <Layers className="w-6 h-6 animate-pulse" />
        </div>
        <h3 className="font-mono text-base font-bold text-slate-300">
          PORTFOLIO CANVAS STANDBY
        </h3>
        <p className="font-mono text-xs text-slate-500 max-w-md mx-auto">
          Upload a resume PDF to run the multi-agent generation pipeline, or click &quot;LOAD DEMO&quot; to inspect the pre-generated sample portfolio.
        </p>
      </div>
    );
  }

  // Copy HTML code to clipboard
  const handleCopyCode = async () => {
    try {
      await navigator.clipboard.writeText(portfolio.html_code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy code:', err);
    }
  };

  // Download HTML file
  const handleDownload = () => {
    const blob = new Blob([portfolio.html_code], { type: 'text/html;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${portfolio.full_name.toLowerCase().replace(/\s+/g, '_')}_portfolio.html`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  // Open HTML in new browser tab
  const handleOpenNewTab = () => {
    const blob = new Blob([portfolio.html_code], { type: 'text/html;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    window.open(url, '_blank');
  };

  const getIframeWidthClass = () => {
    switch (deviceWidth) {
      case 'mobile':
        return 'max-w-[390px]';
      case 'tablet':
        return 'max-w-[768px]';
      default:
        return 'w-full';
    }
  };

  return (
    <div className="border-2 border-retro-cyan bg-retro-surface rounded-sm shadow-retro-cyan overflow-hidden flex flex-col">
      {/* Canvas Top Control Bar */}
      <div className="border-b-2 border-retro-cyan bg-retro-panel px-4 py-2.5 flex flex-wrap items-center justify-between gap-3">
        {/* Left: View Mode Tabs */}
        <div className="flex items-center gap-1.5">
          <button
            onClick={() => setViewMode('interactive')}
            className={`px-3 py-1 text-xs font-mono font-bold flex items-center gap-1.5 border transition-all ${
              viewMode === 'interactive'
                ? 'bg-retro-yellow text-black border-black shadow-retro-yellow-sm'
                : 'border-slate-700 text-slate-300 hover:border-slate-500 bg-retro-surface'
            }`}
          >
            <Eye className="w-3.5 h-3.5" />
            REACTIVE MATRIX
          </button>

          <button
            onClick={() => setViewMode('sandbox')}
            className={`px-3 py-1 text-xs font-mono font-bold flex items-center gap-1.5 border transition-all ${
              viewMode === 'sandbox'
                ? 'bg-retro-cyan text-black border-black shadow-retro-yellow-sm'
                : 'border-slate-700 text-slate-300 hover:border-slate-500 bg-retro-surface'
            }`}
          >
            <Monitor className="w-3.5 h-3.5" />
            SANDBOX HTML
          </button>

          <button
            onClick={() => setViewMode('code')}
            className={`px-3 py-1 text-xs font-mono font-bold flex items-center gap-1.5 border transition-all ${
              viewMode === 'code'
                ? 'bg-retro-magenta text-white border-black shadow-retro-yellow-sm'
                : 'border-slate-700 text-slate-300 hover:border-slate-500 bg-retro-surface'
            }`}
          >
            <Code2 className="w-3.5 h-3.5" />
            RAW CODE
          </button>
        </div>

        {/* Center: Device Switchers (for sandbox mode) */}
        {viewMode === 'sandbox' && (
          <div className="flex items-center gap-1 bg-black/40 border border-slate-700 p-0.5 rounded">
            <button
              onClick={() => setDeviceWidth('desktop')}
              className={`p-1 rounded ${
                deviceWidth === 'desktop'
                  ? 'bg-retro-cyan text-black'
                  : 'text-slate-400 hover:text-white'
              }`}
              title="Desktop View"
            >
              <Monitor className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => setDeviceWidth('tablet')}
              className={`p-1 rounded ${
                deviceWidth === 'tablet'
                  ? 'bg-retro-cyan text-black'
                  : 'text-slate-400 hover:text-white'
              }`}
              title="Tablet View"
            >
              <Tablet className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => setDeviceWidth('mobile')}
              className={`p-1 rounded ${
                deviceWidth === 'mobile'
                  ? 'bg-retro-cyan text-black'
                  : 'text-slate-400 hover:text-white'
              }`}
              title="Mobile View"
            >
              <Smartphone className="w-3.5 h-3.5" />
            </button>
          </div>
        )}

        {/* Right: Actions */}
        <div className="flex items-center gap-2">
          <button
            onClick={handleCopyCode}
            className="px-2.5 py-1 text-xs font-mono border border-slate-700 hover:border-retro-cyan text-slate-300 hover:text-retro-cyan bg-retro-surface flex items-center gap-1.5"
            title="Copy HTML"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-retro-green" /> : <Copy className="w-3.5 h-3.5" />}
            <span>{copied ? 'COPIED!' : 'COPY HTML'}</span>
          </button>

          <button
            onClick={handleDownload}
            className="px-2.5 py-1 text-xs font-mono border border-retro-yellow bg-retro-yellow text-black font-bold hover:bg-yellow-400 flex items-center gap-1.5 shadow-retro-yellow-sm active:translate-x-0.5 active:translate-y-0.5"
            title="Download Standalone HTML"
          >
            <Download className="w-3.5 h-3.5" />
            <span>EXPORT</span>
          </button>

          <button
            onClick={handleOpenNewTab}
            className="p-1 text-slate-400 hover:text-retro-cyan border border-slate-700 bg-retro-surface"
            title="Open In New Window"
          >
            <ExternalLink className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Canvas View Content */}
      <div className="flex-1 bg-retro-bg min-h-[600px] overflow-y-auto retro-scroll">
        {/* VIEW 1: Reactive UI Components */}
        {viewMode === 'interactive' && (
          <div className="space-y-4">
            <HeroSection portfolio={portfolio} />
            <StorySection experience={portfolio.experience} />
            <ProjectGrid projects={portfolio.projects} />

            {/* Additional Info Footer */}
            <div className="p-6 bg-retro-panel border-t border-slate-800 text-center space-y-2">
              <p className="font-mono text-xs text-slate-400">
                SEO Discovered Vectors: {portfolio.seo_keywords.join(' • ')}
              </p>
              {portfolio.review_notes && (
                <p className="font-mono text-xs text-retro-green/80 italic">
                  QA Auditor: {portfolio.review_notes}
                </p>
              )}
            </div>
          </div>
        )}

        {/* VIEW 2: Sandboxed HTML Iframe */}
        {viewMode === 'sandbox' && (
          <div className="p-4 flex justify-center items-start min-h-[700px] bg-slate-950/60">
            <div
              className={`w-full ${getIframeWidthClass()} transition-all duration-300 border-2 border-slate-700 shadow-2xl bg-white rounded overflow-hidden`}
            >
              <div className="bg-slate-800 px-3 py-1.5 flex items-center justify-between text-xs font-mono text-slate-300">
                <span className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-red-500" />
                  <span className="w-2 h-2 rounded-full bg-yellow-500" />
                  <span className="w-2 h-2 rounded-full bg-green-500" />
                  <span className="ml-2 text-slate-400">https://portfolio.local/preview</span>
                </span>
                <span className="text-[10px] uppercase text-retro-cyan font-bold">
                  {deviceWidth} mode
                </span>
              </div>
              <iframe
                title="Generated Portfolio HTML Sandbox"
                srcDoc={portfolio.html_code}
                className="w-full h-[700px] border-0"
                sandbox="allow-scripts allow-same-origin"
              />
            </div>
          </div>
        )}

        {/* VIEW 3: Raw Code Inspector */}
        {viewMode === 'code' && (
          <div className="p-4 space-y-4">
            <div className="flex items-center justify-between">
              <RetroBadge variant="cyan" size="sm">
                Generated HTML ({portfolio.html_code.length} characters)
              </RetroBadge>
              <button
                onClick={handleCopyCode}
                className="text-xs font-mono text-retro-yellow hover:underline flex items-center gap-1"
              >
                <Copy className="w-3 h-3" />
                Copy to Clipboard
              </button>
            </div>
            <pre className="p-4 bg-black/95 text-retro-green font-mono text-xs overflow-x-auto border border-retro-green/30 rounded retro-scroll max-h-[650px] selection:bg-retro-green selection:text-black">
              <code>{portfolio.html_code}</code>
            </pre>
          </div>
        )}
      </div>
    </div>
  );
};

