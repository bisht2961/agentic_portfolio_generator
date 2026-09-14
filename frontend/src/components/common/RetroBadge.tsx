import React from 'react';

interface RetroBadgeProps {
  children: React.ReactNode;
  variant?: 'cyan' | 'yellow' | 'green' | 'magenta' | 'slate' | 'outline';
  size?: 'sm' | 'md';
  icon?: React.ReactNode;
  className?: string;
}

export const RetroBadge: React.FC<RetroBadgeProps> = ({
  children,
  variant = 'cyan',
  size = 'md',
  icon,
  className = '',
}) => {
  const sizeClasses = {
    sm: 'px-2 py-0.5 text-[11px]',
    md: 'px-3 py-1 text-xs',
  };

  const variantClasses = {
    cyan: 'bg-cyan-950/70 text-retro-cyan border-retro-cyan hover:bg-cyan-900/60',
    yellow: 'bg-yellow-950/70 text-retro-yellow border-retro-yellow hover:bg-yellow-900/60',
    green: 'bg-emerald-950/70 text-retro-green border-retro-green hover:bg-emerald-900/60',
    magenta: 'bg-pink-950/70 text-retro-magenta border-retro-magenta hover:bg-pink-900/60',
    slate: 'bg-slate-800/80 text-slate-300 border-slate-600 hover:bg-slate-700/80',
    outline: 'bg-transparent text-slate-300 border-slate-500 hover:border-slate-300',
  };

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border font-mono font-medium uppercase tracking-wider transition-colors select-none ${sizeClasses[size]} ${variantClasses[variant]} ${className}`}
    >
      {icon && <span className="text-current opacity-80">{icon}</span>}
      <span>{children}</span>
    </span>
  );
};

