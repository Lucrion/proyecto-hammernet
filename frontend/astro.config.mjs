import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';
import node from '@astrojs/node';

// https://astro.build/config
export default defineConfig({
  integrations: [tailwind()],
  output: 'static',
  adapter: node({
    mode: 'standalone'
  }),
  server: {
    host: true,
    port: 4321
  },
  vite: {
    assetsInclude: ['**/*.webp', '**/*.svg', '**/*.png', '**/*.jpg', '**/*.jpeg'],
    server: {
      proxy: {
        '/api': {
          target: process.env.PUBLIC_API_URL_PRODUCTION || 'http://localhost:8000',
          changeOrigin: true,
          secure: false,
          ws: true
        }
      }
    }
  },
  build: {
    inlineStylesheets: 'auto'
  }
});