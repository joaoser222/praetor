import path from 'path'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Host local servido pelo Caddy no desenvolvimento (docker/caddy/Caddyfile.dev).
const devDomain = process.env.DEV_DOMAIN ?? 'localhost'
// Alvo do proxy /api quando o SPA é acessado direto pelo dev server (5173).
const apiProxyTarget = process.env.VITE_PROXY_TARGET ?? 'http://localhost:8000'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    // O SPA chama /api/* na mesma origem: via Caddy, ou por este proxy quando
    // o acesso é direto em http://localhost:5173.
    proxy: {
      '/api': {
        target: apiProxyTarget,
        changeOrigin: true,
      },
    },
    // O Vite recusa hosts desconhecidos; o Caddy acessa o dev server por DEV_DOMAIN.
    allowedHosts: [devDomain, 'localhost', '127.0.0.1'],
  },
})
