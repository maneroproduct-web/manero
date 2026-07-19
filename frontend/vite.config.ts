import { fileURLToPath, URL } from 'node:url'

import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    port: 5173,
    // Fail loudly if 5173 is taken rather than silently drifting to 5174 —
    // otherwise the documented URL quietly points at nothing.
    strictPort: true,
    proxy: {
      // Same-origin in dev, so CORS never enters the picture locally.
      // 127.0.0.1, not localhost: on Windows localhost resolves to ::1 first,
      // but uvicorn binds IPv4 only — the proxy would intermittently fail with
      // ECONNREFUSED against a perfectly healthy API.
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
})
