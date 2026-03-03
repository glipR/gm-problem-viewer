import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { readFileSync } from 'fs'
import { resolve } from 'path'

function loadConfig(): Record<string, string> {
  try {
    const raw = readFileSync(resolve(__dirname, '..', 'config.yaml'), 'utf-8')
    const result: Record<string, string> = {}
    for (const line of raw.split('\n')) {
      const match = line.match(/^(\w+)\s*:\s*(.+?)(?:\s*#.*)?$/)
      if (match) result[match[1]] = match[2].trim()
    }
    return result
  } catch {
    return {}
  }
}

const cfg = loadConfig()

const backendPort = process.env.PORT || cfg.port || '8001'
const frontendPort = parseInt(process.env.FRONTEND_PORT || cfg.frontend_port || '5173', 10)

export default defineConfig({
  plugins: [react()],
  server: {
    port: frontendPort,
    proxy: {
      '/api': {
        target: `http://localhost:${backendPort}`,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
})
