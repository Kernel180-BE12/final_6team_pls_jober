import { fileURLToPath, URL } from 'node:url'
import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // root 폴더의 .env 파일 로드
  const env = loadEnv(mode, process.cwd() + '/../', '')
  
  return {
    plugins: [
      vue(),
    ],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url))
      }
    },
    server: {
      port: 3000,
      proxy: {
        '/api': {
          target: env.VITE_API_BASE_URL || 'http://localhost:8080',
          changeOrigin: true
        },
        '/ai': {
          target: env.VITE_AI_BASE_URL || 'http://localhost:8000',
          changeOrigin: true
        }
      }
    },
    define: {
      __API_BASE_URL__: JSON.stringify(env.VITE_API_BASE_URL || 'http://localhost:8080'),
      __AI_BASE_URL__: JSON.stringify(env.VITE_AI_BASE_URL || 'http://localhost:8000')
    }
  }
})

