import React from 'react';
import { Sun, Moon } from 'lucide-react';
import { usePortfolioStore } from '../../store/usePortfolioStore';

export const ThemeToggle: React.FC = () => {
  const { uiTheme, toggleUiTheme } = usePortfolioStore();

  const isDark = uiTheme === 'dark';

  return (
    <button
      type="button"
      onClick={toggleUiTheme}
      aria-label={`Switch to ${isDark ? 'light' : 'dark'} mode`}
      title={`Current: ${uiTheme.toUpperCase()} mode. Click to switch to ${isDark ? 'LIGHT' : 'DARK'} mode.`}
      className={`relative inline-flex items-center gap-2 px-2.5 sm:px-3 py-1 border-2 transition-all duration-100 select-none cursor-pointer active:translate-x-[2px] active:translate-y-[2px] font-pixel text-[9px] sm:text-[10px] uppercase tracking-wider ${
        isDark
          ? 'bg-retro-panel border-retro-cyan text-retro-yellow shadow-retro-yellow-sm hover:bg-slate-800'
          : 'bg-[#F5F3E9] border-[#1C1917] text-[#15803D] shadow-[2px_2px_0px_#000000] hover:bg-[#E2EDF8]'
      }`}
    >
      {isDark ? (
        <>
          <Moon className="w-3.5 h-3.5 text-retro-cyan" />
          <span>DARK</span>
          <span className="w-2 h-2 rounded-full bg-retro-cyan animate-pulse" />
        </>
      ) : (
        <>
          <Sun className="w-3.5 h-3.5 text-[#EAB308]" />
          <span>LIGHT</span>
          <span className="w-2 h-2 rounded-full bg-[#15803D]" />
        </>
      )}
    </button>
  );
};

