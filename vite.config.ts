import { defineConfig } from 'vite';
import react            from '@vitejs/plugin-react';

/**
 * vite.config.ts — web-app branch
 * Pure Vite SPA config. No Tauri plugin or env vars.
 *
 * Dev server proxies /api/* to the Python backend at :8008
 * so fetch('/api/alignment') works without CORS headers in dev.
 * In production, configure your reverse proxy (nginx / Caddy /
 * Cloudflare) to route /api/* to the backend service.
 */
export default defineConfig({
  plugins: [react()],

  server: {
    port:        3000,
    strictPort:  false,
    open:        true,   // open browser on `vite dev`
    proxy: {
      '/api': {
        target:       'http://localhost:8008',
        changeOrigin: true,
        rewrite:      (path) => path.replace(/^\/api/, ''),
      },
    },
  },

  build: {
    outDir:          'dist',
    sourcemap:       true,
    rollupOptions: {
      output: {
        // Split Three.js into its own chunk — it's large (~600 kB)
        manualChunks: {
          three: ['three'],
          gsap:  ['gsap'],
        },
      },
    },
  },
});
