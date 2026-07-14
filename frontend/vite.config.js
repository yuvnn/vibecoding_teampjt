import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// 개발 서버에서 /api 요청을 로컬 FastAPI(8000)로 프록시.
// 배포 시에는 VITE_API_BASE_URL(.env)로 Render 백엔드 URL을 직접 지정.
export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
