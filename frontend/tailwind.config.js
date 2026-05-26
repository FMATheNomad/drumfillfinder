/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        drum: {
          kick: "#ef4444",
          snare: "#22c55e",
          "hi-hat": "#3b82f6",
        },
      },
    },
  },
  plugins: [],
}
