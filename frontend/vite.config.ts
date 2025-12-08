import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'
import { execSync } from 'child_process'

// Get git commit hash
const getGitHash = () => {
  try {
    return execSync('git rev-parse --short HEAD').toString().trim()
  } catch (e) {
    return 'unknown'
  }
}

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  define: {
    __GIT_HASH__: JSON.stringify(getGitHash()),
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5174,
    proxy: {
      '/api': {
        // Backend Django server for dev (sopira.magic)
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/pdfdev': {
        // Serve PDF documents from Django in dev via the same origin
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})

