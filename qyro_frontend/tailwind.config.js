/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          bg: "#F8FAFC", // Off-white clean background
          card: "#FFFFFF", // Translucent clean white card
          indigo: "#6366F1", // Soft Indigo
          cyan: "#06B6D4", // Subtle Cyan
          dark: "#0F172A", // Slate dark text
          muted: "#64748B", // Muted slate gray text
        }
      },
      fontFamily: {
        sans: ["Inter", "sans-serif"],
      },
      scale: {
        '102': '1.02',
      }
    },
  },
  plugins: [],
}
