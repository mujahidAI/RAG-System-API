/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        sidebar: '#1e1e2e',
        main: '#f8f8f8',
        accent: '#6366f1',
        'accent-hover': '#4f46e5',
      }
    },
  },
  plugins: [],
}
