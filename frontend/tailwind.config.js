/** @type {import('tailwindcss').Config} */
export default {
  content: ["./src/**/*.{html,jsx,js}", "index.html"],
  safelist: [
    {pattern: /opacity-+/}
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}

