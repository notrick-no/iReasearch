import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'

export default defineConfig({
  plugins: [vue(),
       // 自动导入 API
       AutoImport({
        imports: ['vue', 'vue-router'],
        resolvers: [ElementPlusResolver()],
        // 可选：生成 types 文件，支持 TS 智能提示
        dts: 'src/auto-imports.d.ts',
        eslintrc: {
          enabled: false // 若使用 ESLint，可设为 true 自动生成配置
        }
      }),
      // 自动导入组件
      Components({
        resolvers: [ElementPlusResolver()],
        // 可选：生成 types 文件
        dts: 'src/components.d.ts'
      })
  ],
  server: {
    port: 5173,
    host: true, // 👈 允许外部访问
    allowedHosts: ['.trycloudflare.com'],
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true
      }
    }
  },
  build: {
    outDir: '../backend/static',
    emptyOutDir: true
  }
})
