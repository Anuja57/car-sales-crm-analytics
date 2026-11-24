/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Poppins', 'sans-serif'],
      },
      colors: {
        mint:  { DEFAULT: 'rgb(240,253,244)', dark: 'rgb(220,252,231)' },
        brand: { DEFAULT: '#1D4ED8', dark: '#1E40AF' },
      },
    },
  },
  plugins: [],
}
