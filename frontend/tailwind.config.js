/** @type {import('tailwindcss').Config} */
import forms from '@tailwindcss/forms';
import containerQueries from '@tailwindcss/container-queries';
export default {
  darkMode: "class",
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        "primary": "#326669",
        "primary-light": "#D5E3EB",
        "background-light": "#f6f7f7",
        
        "surface-container-highest": "#e1e3e2",
        "outline": "#326669",
        "on-secondary-container": "#536667",
        "surface-bright": "#ffffff",
        "primary-fixed": "#b7ecef",
        "on-tertiary-fixed-variant": "#673c24",
        "secondary-container": "#cfe4e5",
        "secondary-fixed-dim": "#b6cacb",
        "on-background": "#0f172a",
        "primary-fixed-dim": "#9bd0d3",
        "on-tertiary": "#ffffff",
        "on-error": "#ffffff",
        "on-primary-fixed": "#002021",
        "tertiary-container": "#815238",
        "tertiary": "#663b23",
        "surface-dim": "#d9dada",
        "surface": "#f6f7f7",
        "on-error-container": "#93000a",
        "secondary-fixed": "#d2e6e7",
        "inverse-primary": "#9bd0d3",
        "surface-container": "#D5E3EB",
        "inverse-surface": "#151c1d",
        "tertiary-fixed": "#ffdbca",
        "surface-container-lowest": "#ffffff",
        "on-secondary-fixed-variant": "#374a4b",
        "on-secondary": "#ffffff",
        "inverse-on-surface": "#f0f1f0",
        "on-primary-container": "#326669",
        "on-secondary-fixed": "#0c1e20",
        "on-tertiary-fixed": "#321201",
        "on-surface": "#0f172a",
        "error-container": "#ffdad6",
        "on-primary": "#ffffff",
        "outline-variant": "rgba(50, 102, 105, 0.1)",
        "primary-container": "#D5E3EB",
        "tertiary-fixed-dim": "#f7b999",
        "background": "#f6f7f7",
        "surface-tint": "#326669",
        "surface-container-high": "#e7e8e8",
        "surface-variant": "#D5E3EB",
        "on-tertiary-container": "#ffccb2",
        "secondary": "#4f6263",
        "on-primary-fixed-variant": "#164e51",
        "error": "#ba1a1a",
        "on-surface-variant": "#475569",
        "surface-container-low": "#f6f7f7"
      },
      fontFamily: {
        "display": ["Inter", "sans-serif"],
        "headline": ["Inter", "sans-serif"],
        "body": ["Inter", "sans-serif"],
        "label": ["Inter", "sans-serif"]
      },
      borderRadius: {
        "DEFAULT": "0.25rem", 
        "lg": "0.5rem", 
        "xl": "0.75rem", 
        "2xl": "1rem", 
        "full": "9999px"
      },
    },
  },
  plugins: [
    forms,
    containerQueries
  ],
}
