import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  // For GitHub Pages: set base to repo name if deploying to username.github.io/repo-name
  // Override with VITE_BASE_URL env var, e.g. VITE_BASE_URL=/gm-problem-viewer/
  base: process.env.VITE_BASE_URL || '/',
})
