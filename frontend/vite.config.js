import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

const apiRoutes = [
  '/auth',
  '/users',
  '/waste',
  '/pickup',
  '/collector',
  '/recycler',
  '/admin',
  '/notifications',
  '/config',
  '/system',
  '/uploads',
  '/docs',
  '/openapi.json',
];

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: Object.fromEntries(
      apiRoutes.map((route) => [
        route,
        {
          target: 'http://127.0.0.1:8000',
          changeOrigin: true,
        },
      ]),
    ),
  },
});
