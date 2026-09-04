/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      fontFamily: {
        display: ["Sora", "system-ui", "sans-serif"],
        body: ["Inter", "system-ui", "sans-serif"],
      },
      colors: {
        // Paleta de marca: blancos, lilas suaves y morado profundo.
        brand: {
          50: "#faf8fd",
          100: "#f3eefb",
          200: "#e6dbf7",
          300: "#d2bcf0",
          400: "#b892e3",
          500: "#9c6ed4",
          600: "#7f4dc0",
          700: "#653c9c",
          800: "#4c2a85",
          900: "#33195e",
          950: "#1f0f3d",
        },
        ink: {
          50: "#f7f6f9",
          100: "#efeef3",
          400: "#8b839a",
          500: "#6b6478",
          700: "#3f3850",
          900: "#1f0f3d",
        },
      },
      boxShadow: {
        soft: "0 1px 2px 0 rgba(31, 15, 61, 0.06), 0 8px 24px -8px rgba(31, 15, 61, 0.12)",
      },
      borderRadius: {
        xl2: "0.875rem",
      },
    },
  },
  plugins: [],
};
