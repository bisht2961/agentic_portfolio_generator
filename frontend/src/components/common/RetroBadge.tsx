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
    cyan: 'bg-sky-100 text-[#0284C7] border-[#0284C7] dark:bg-cyan-950/70 dark:text-retro-cyan dark:border-retro-cyan hover:opacity-90',
    yellow: 'bg-amber-100 text-[#CA8A04] border-[#EAB308] dark:bg-yellow-950/70 dark:text-retro-yellow dark:border-retro-yellow hover:opacity-90',
    green: 'bg-emerald-100 text-[#15803D] border-[#15803D] dark:bg-emerald-950/70 dark:text-retro-green dark:border-retro-green hover:opacity-90',
    magenta: 'bg-pink-100 text-pink-700 border-pink-400 dark:bg-pink-950/70 dark:text-retro-magenta dark:border-retro-magenta hover:opacity-90',
    slate: 'bg-retro-input-inactive text-retro-body border-retro-border dark:bg-slate-800/80 dark:text-slate-300 dark:border-slate-600 hover:opacity-90',
    outline: 'bg-transparent text-retro-body border-retro-border hover:border-retro-cyan',
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

