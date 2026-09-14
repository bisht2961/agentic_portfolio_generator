/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        retro: {
          bg: '#0a0d14',
          surface: '#111726',
          panel: '#161f33',
          border: '#1e293b',
          cyan: '#00f0ff',
          'cyan-dim': 'rgba(0, 240, 255, 0.15)',
          yellow: '#ffe600',
          'yellow-hover': '#ffd000',
          magenta: '#ff007f',
          green: '#00ff66',
          muted: '#8b9bb4',
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
        'retro-cyan': '4px 4px 0px 0px #000000, 0 0 15px rgba(0, 240, 255, 0.3)',
        'retro-magenta': '4px 4px 0px 0px #000000, 0 0 15px rgba(255, 0, 127, 0.3)',
        'hard-dark': '5px 5px 0px 0px #000000',
      },
      borderWidth: {
        '3': '3px',
      }
    },
  },
  plugins: [],
}

