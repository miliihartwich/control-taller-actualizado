// vite.config.js
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    host: true,      // necesario en Docker
    port: 5173,
    proxy: {
      '/api': {
        // ⬇️ IMPORTANTE: en docker-compose el backend es "http://backend:8000"
        // (si pusieras localhost, apunta al contenedor del frontend, no al backend)
        target: 'http://backend:8000',
        changeOrigin: true,
        // /api/login -> /login (Flask lo tiene en raíz)
        rewrite: (p) => p.replace(/^\/api/, ''),
      },
    },
  },
  build: {
    minify: 'terser',   // usamos Terser en lugar de esbuild
    target: 'es2019',   // evita transforms raros con optional chaining
    terserOptions: {
      compress: {
        passes: 2,
        unsafe: false,
      },
    },
  },
})

