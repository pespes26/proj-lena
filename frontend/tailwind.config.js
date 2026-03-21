/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js}'],
  theme: {
    extend: {
      colors: {
        ios: {
          blue: '#007AFF',
          'blue-dark': '#0056CC',
          'blue-light': '#E8F0FE',
          gray: { 1: '#8E8E93', 2: '#AEAEB2', 3: '#C7C7CC', 4: '#D1D1D6', 5: '#E5E5EA', 6: '#F2F2F7' },
          red: '#FF3B30',
          green: '#34C759',
          orange: '#FF9500',
          yellow: '#FFCC00',
          purple: '#AF52DE',
          teal: '#5AC8FA',
          bg: '#F2F2F7',
        },
      },
      borderRadius: {
        'ios': '16px',
        'ios-lg': '20px',
      },
      boxShadow: {
        'ios': '0 1px 3px rgba(0,0,0,0.04), 0 4px 12px rgba(0,0,0,0.03)',
        'ios-lg': '0 2px 8px rgba(0,0,0,0.06), 0 8px 24px rgba(0,0,0,0.04)',
      },
    },
  },
  plugins: [],
}
