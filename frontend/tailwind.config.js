/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#e6f1ff',
          100: '#b3d7ff',
          200: '#80bdff',
          300: '#4da3ff',
          400: '#1a89ff',
          500: '#0070e0',
          600: '#0056b3',
          700: '#003d80',
          800: '#00244d',
          900: '#000b1a',
        },
        mspbs: {
          primary: '#003366',
          secondary: '#006699',
          accent: '#0099CC',
          success: '#28a745',
          warning: '#ffc107',
          danger: '#dc3545',
        }
      },
    },
  },
  plugins: [],
}
