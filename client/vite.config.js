import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import mkcert from 'vite-plugin-mkcert'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  // HTTPS by default; the end-to-end tests turn it off so CI needs no local CA.
  const https = env.VITE_HTTPS !== 'false'
  return {
    plugins: [react(), tailwindcss(), https && mkcert()],
    server: {
      https,
      host: true,
      proxy: {
        '/api': {
          target: env.VITE_API_TARGET || 'http://localhost:8000',
          changeOrigin: true,
        },
      },
      // File change events don't cross the Docker bind mount on Windows.
      watch: { usePolling: true },
    },
  }
})
