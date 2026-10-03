function withOpacity(variableName) {
  return ({ opacityValue }) => {
    if (opacityValue !== undefined) {
      return `rgba(var(${variableName}), ${opacityValue})`;
    }
    return `rgb(var(${variableName}))`;
  };
}

/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        retro: {
          bg: withOpacity('--canvas-bg-rgb'),
          surface: withOpacity('--card-surface-bg-rgb'),
          panel: withOpacity('--panel-bg-rgb'),
          border: withOpacity('--border-neutral-rgb'),
          'border-structural': withOpacity('--border-structural-rgb'),
          cyan: withOpacity('--color-cyan-rgb'),
          'cyan-dim': 'rgba(var(--color-cyan-rgb), 0.15)',
          yellow: withOpacity('--color-yellow-rgb'),
          'yellow-hover': withOpacity('--color-yellow-hover-rgb'),
          magenta: withOpacity('--color-magenta-rgb'),
          green: withOpacity('--color-green-rgb'),
          muted: withOpacity('--muted-text-rgb'),
          body: withOpacity('--primary-body-text-rgb'),
          heading: withOpacity('--pixel-heading-text-rgb'),
          cta: withOpacity('--action-accent-rgb'),
          'cta-hover': withOpacity('--action-hover-rgb'),
          input: withOpacity('--input-field-fill-rgb'),
          'input-inactive': withOpacity('--input-inactive-fill-rgb'),
          rivet: withOpacity('--corner-rivet-rgb'),
        },
      },
      fontFamily: {
        mono: ['"JetBrains Mono"', '"Fira Code"', 'ui-monospace', 'monospace'],
        pixel: ['"Press Start 2P"', 'monospace'],
        display: ['"Space Grotesk"', 'sans-serif'],
      },
      boxShadow: {
        'retro-yellow': '4px 4px 0px 0px #000000',
        'retro-yellow-sm': '2px 2px 0px 0px #000000',
        'retro-cyan': '4px 4px 0px 0px #000000, 0 0 15px rgba(var(--color-cyan-rgb), 0.3)',
        'retro-magenta': '4px 4px 0px 0px #000000, 0 0 15px rgba(var(--color-magenta-rgb), 0.3)',
        'hard-dark': '4px 4px 0px 0px #000000',
      },
      borderWidth: {
        '3': '3px',
      }
    },
  },
  plugins: [],
}

