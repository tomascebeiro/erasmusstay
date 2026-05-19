/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#e94560",
        dark: "#0f3460",
        darker: "#16213e",
        darkest: "#1a1a2e",
      },
    },
  },
  plugins: [],
}