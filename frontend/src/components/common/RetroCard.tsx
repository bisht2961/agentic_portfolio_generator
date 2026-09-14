import React from 'react';

interface RetroCardProps {
  title?: string;
  subtitle?: string;
  icon?: React.ReactNode;
  headerAction?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
  glow?: boolean;
  scanlines?: boolean;
}

// Rivet screw element with 8-bit metallic look
const CornerRivet = ({ position }: { position: 'tl' | 'tr' | 'bl' | 'br' }) => {
  const posClasses = {
    tl: 'top-1.5 left-1.5',
    tr: 'top-1.5 right-1.5',
    bl: 'bottom-1.5 left-1.5',
    br: 'bottom-1.5 right-1.5',
  };

  return (
    <div
      className={`absolute ${posClasses[position]} w-2 h-2 rounded-full bg-slate-600 border border-black flex items-center justify-center pointer-events-none z-10 shadow-inner`}
      title="Rivet"
    >
      <div className="w-1 h-[1px] bg-slate-400 rotate-45" />
    </div>
  );
};

export const RetroCard: React.FC<RetroCardProps> = ({
  title,
  subtitle,
  icon,
  headerAction,
  children,
  className = '',
  glow = false,
  scanlines = false,
}) => {
  return (
    <div
      className={`relative bg-retro-surface border-2 border-retro-cyan shadow-hard-dark rounded-sm transition-all duration-200 ${
        glow ? 'shadow-retro-cyan' : ''
      } ${scanlines ? 'crt-scanlines' : ''} ${className}`}
    >
      {/* 4 Corner Rivets */}
      <CornerRivet position="tl" />
      <CornerRivet position="tr" />
      <CornerRivet position="bl" />
      <CornerRivet position="br" />

      {/* Header bar if title provided */}
      {title && (
        <div className="border-b-2 border-retro-cyan bg-retro-panel px-4 py-2 flex items-center justify-between">
          <div className="flex items-center gap-2">
            {icon && <span className="text-retro-cyan">{icon}</span>}
            <div>
              <h3 className="font-mono font-bold text-sm text-retro-cyan uppercase tracking-wider">
                {title}
              </h3>
              {subtitle && (
                <p className="text-[11px] text-slate-400 font-mono">{subtitle}</p>
              )}
            </div>
          </div>
          {headerAction && <div>{headerAction}</div>}
        </div>
      )}

      {/* Card Body */}
      <div className="p-4 sm:p-5">{children}</div>
    </div>
  );
};

