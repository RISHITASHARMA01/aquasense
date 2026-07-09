/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        aqua: {
          50: '#eefbff',
          100: '#d9f4ff',
          200: '#b8eaff',
          300: '#84dcff',
          400: '#48c6ff',
          500: '#1eabf5',
          600: '#0f8cd1',
          700: '#0f70a8',
          800: '#135e8a',
          900: '#144f73',
        },
      },
    },
  },
  plugins: [],
}
