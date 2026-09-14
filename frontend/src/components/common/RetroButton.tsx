import React from 'react';

interface RetroButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'yellow' | 'cyan' | 'magenta' | 'dark';
  size?: 'sm' | 'md' | 'lg';
  pixel?: boolean;
  children: React.ReactNode;
}

export const RetroButton: React.FC<RetroButtonProps> = ({
  variant = 'yellow',
  size = 'md',
  pixel = false,
  className = '',
  disabled = false,
  children,
  ...props
}) => {
  const baseStyles = 
    'inline-flex items-center justify-center font-bold tracking-wider uppercase transition-all duration-100 select-none border-2 border-black active:translate-x-[2px] active:translate-y-[2px]';

  const sizeStyles = {
    sm: 'px-3 py-1 text-xs gap-1.5',
    md: 'px-5 py-2.5 text-sm gap-2',
    lg: 'px-7 py-3 text-base gap-2.5',
  };

  const variantStyles = {
    yellow: 'bg-retro-yellow text-black hover:bg-retro-yellow-hover shadow-retro-yellow active:shadow-retro-yellow-sm',
    cyan: 'bg-retro-cyan text-black hover:bg-cyan-300 shadow-retro-yellow active:shadow-retro-yellow-sm',
    magenta: 'bg-retro-magenta text-white hover:bg-pink-600 shadow-retro-yellow active:shadow-retro-yellow-sm',
    dark: 'bg-retro-surface text-retro-cyan border-retro-cyan hover:bg-retro-panel shadow-[4px_4px_0px_#000]',
  };

  const disabledStyles = disabled
    ? 'opacity-50 cursor-not-allowed hover:bg-inherit active:translate-x-0 active:translate-y-0 shadow-none'
    : 'cursor-pointer';

  const fontStyle = pixel ? 'font-pixel text-[11px]' : 'font-mono';

  return (
    <button
      disabled={disabled}
      className={`${baseStyles} ${sizeStyles[size]} ${variantStyles[variant]} ${disabledStyles} ${fontStyle} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
};

