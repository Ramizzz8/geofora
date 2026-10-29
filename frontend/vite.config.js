import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: { '/api': 'http://localhost:8000' },
    // copia dañada por OneDrive que Windows no deja borrar: el vigilante de Vite no debe entrar
    watch: { ignored: ['**/node_modules_roto/**'] },
  },
  test: { environment: 'jsdom', setupFiles: './src/test-setup.js', globals: true },
})
