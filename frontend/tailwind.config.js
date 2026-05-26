/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: {
          50: "#f0fdf4",
          100: "#dcfce7",
          200: "#bbf7d0",
          300: "#86efac",
          400: "#4ade80",
          500: "#22c55e",
          600: "#16a34a",
          700: "#15803d",
          800: "#166534",
          900: "#14532d",
          950: "#052e16",
        },
        forest: {
          light: "#dcfce7",
          mid: "#86efac",
          base: "#22c55e",
          dark: "#166534",
          deep: "#14532d",
        },
      },
      fontFamily: {
        sans: ["'DM Sans'", "sans-serif"],
        display: ["'Syne'", "sans-serif"],
        mono: ["'JetBrains Mono'", "monospace"],
      },
      backgroundImage: {
        "green-mesh":
          "radial-gradient(at 40% 20%, hsla(151,80%,90%,0.8) 0px, transparent 50%), radial-gradient(at 80% 0%, hsla(142,70%,85%,0.6) 0px, transparent 50%), radial-gradient(at 0% 50%, hsla(160,60%,88%,0.7) 0px, transparent 50%)",
      },
      boxShadow: {
        glass: "0 8px 32px 0 rgba(22, 101, 52, 0.1)",
        "green-glow": "0 0 20px rgba(34, 197, 94, 0.3)",
      },
    },
  },
  plugins: [],
};
