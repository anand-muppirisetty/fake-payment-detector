/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        // Forensic / security themed palette — deep ink base with a
        // "verification cyan" accent and signal colors for verdicts.
        ink: {
          950: "#070b14",
          900: "#0c1220",
          800: "#121a2c",
          700: "#1b2540",
          600: "#293457",
        },
        mist: {
          100: "#f4f7fb",
          200: "#e6ebf3",
          300: "#c9d3e3",
          400: "#93a2c0",
        },
        signal: {
          cyan: "#33d6c0",
          cyanDim: "#1f8f80",
          amber: "#f5a623",
          red: "#ef4a5f",
          green: "#3ecf8e",
        },
      },
      fontFamily: {
        display: ["'Space Grotesk'", "system-ui", "sans-serif"],
        body: ["'Inter'", "system-ui", "sans-serif"],
        mono: ["'JetBrains Mono'", "ui-monospace", "monospace"],
      },
      boxShadow: {
        glow: "0 0 0 1px rgba(51,214,192,0.15), 0 8px 30px -8px rgba(51,214,192,0.25)",
      },
      backgroundImage: {
        "grid-fade":
          "linear-gradient(to bottom, transparent, rgba(7,11,20,1)), repeating-linear-gradient(0deg, rgba(255,255,255,0.035) 0px, transparent 1px, transparent 40px), repeating-linear-gradient(90deg, rgba(255,255,255,0.035) 0px, transparent 1px, transparent 40px)",
      },
    },
  },
  plugins: [],
};
