/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        carbon: {
          DEFAULT: '#090A0F',
          surface: '#11131A',
          card: '#161922',
          cardHover: '#1C202C',
          border: 'rgba(255, 255, 255, 0.07)',
          highlight: 'rgba(255, 255, 255, 0.12)',
        },
        indigo: {
          electric: '#6366F1',
          hover: '#4F46E5',
        },
      },
      fontFamily: {
        sans: ['Inter', 'Geist Sans', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
        mono: ['JetBrains Mono', 'Geist Mono', 'monospace'],
      },
    },
  },
  plugins: [],
}
