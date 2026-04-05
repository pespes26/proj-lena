/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js}'],
  theme: {
    extend: {
      fontFamily: {
        // Unified SaaS stack — DM Sans for Latin, Rubik for Hebrew
        sans: ['"DM Sans"', 'Rubik', '-apple-system', 'BlinkMacSystemFont', 'system-ui', 'sans-serif'],
        display: ['"DM Sans"', 'Rubik', '-apple-system', 'system-ui', 'sans-serif'],
        serif: ['"DM Sans"', 'Rubik', '-apple-system', 'system-ui', 'sans-serif'],
      },
      fontSize: {
        'hero-xl': ['clamp(2.75rem, 5.5vw, 4rem)',   { lineHeight: '1.0',  letterSpacing: '-0.022em' }],
        'hero-lg': ['clamp(2.25rem, 4.5vw, 3.25rem)', { lineHeight: '1.02', letterSpacing: '-0.018em' }],
        'hero-md': ['clamp(1.75rem, 3vw, 2.25rem)',   { lineHeight: '1.05', letterSpacing: '-0.012em' }],
        'hero-sm': ['clamp(1.25rem, 2vw, 1.625rem)',  { lineHeight: '1.1',  letterSpacing: '-0.008em' }],
        'eyebrow': ['0.75rem',  { lineHeight: '1.2', letterSpacing: '0.02em' }],
        'dateline':['0.8125rem',{ lineHeight: '1.2', letterSpacing: '0.01em' }],
      },
      colors: {
        // Canvas
        bg: '#f8fafc',
        surface: {
          DEFAULT: '#ffffff',
          muted: '#f1f5f9',
        },
        // Ink
        ink: {
          DEFAULT: '#0f172a',
          strong: '#020617',
          muted: '#475569',
          faint: '#94a3b8',
        },
        // Lines
        border: {
          DEFAULT: '#e2e8f0',
          strong: '#cbd5e1',
        },
        // Accent — emerald
        accent: {
          DEFAULT: '#059669',
          hover: '#047857',
          soft: '#ecfdf5',
        },
        // Semantic
        positive: {
          DEFAULT: '#059669',
          soft: '#ecfdf5',
        },
        negative: {
          DEFAULT: '#e11d48',
          soft: '#fff1f2',
        },
        warning: {
          DEFAULT: '#d97706',
          soft: '#fffbeb',
        },
        info: '#2563eb',

        // Legacy aliases — retained so template classes using `paper`, `rule`, `ink-*` keep working
        paper: {
          DEFAULT: '#f8fafc',
          light: '#ffffff',
          dark: '#f1f5f9',
        },
        rule: {
          DEFAULT: '#e2e8f0',
          strong: '#cbd5e1',
        },
      },
      maxWidth: {
        app: '1360px',
        issue: '1360px', // legacy alias
      },
      borderRadius: {
        DEFAULT: '8px',
        sm: '6px',
        md: '10px',
        lg: '14px',
        xl: '18px',
        '2xl': '22px',
      },
      boxShadow: {
        'sm': '0 1px 2px 0 rgb(15 23 42 / 0.04), 0 1px 3px 0 rgb(15 23 42 / 0.06)',
        'md': '0 2px 4px -2px rgb(15 23 42 / 0.06), 0 4px 12px -2px rgb(15 23 42 / 0.08)',
        'lg': '0 10px 30px -10px rgb(15 23 42 / 0.18), 0 4px 12px -4px rgb(15 23 42 / 0.08)',
        'xl': '0 20px 48px -16px rgb(15 23 42 / 0.22), 0 8px 24px -8px rgb(15 23 42 / 0.10)',
        'card': '0 1px 2px 0 rgb(15 23 42 / 0.04), 0 1px 3px 0 rgb(15 23 42 / 0.06)',
        'ring-accent': '0 0 0 3px rgba(5, 150, 105, 0.20)',
      },
    },
  },
  plugins: [],
}
