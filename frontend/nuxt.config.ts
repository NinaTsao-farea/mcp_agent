export default defineNuxtConfig({
  // 相容性日期
  compatibilityDate: '2025-10-13',
  
  // 開發工具
  devtools: { enabled: true },
  
  // CSS 框架
  css: ['~/assets/css/main.css'],
  
  // 模組
  modules: [
    '@nuxt/ui',
    '@pinia/nuxt'
  ],
  
  // UI 設定
  ui: {
    global: true
  },

  icon: {
    clientBundle: {
      /* icons: [], */      
      icons: [
          'heroicons:check-circle', 
          'heroicons:check-circle-solid',
          'heroicons:phone-arrow-up-right',
          'heroicons:arrow-path-20-solid',
          'heroicons:arrow-path-solid',
          'heroicons:arrow-right',
          'heroicons:arrow-left',
          'heroicons:arrow-right-solid',
          'heroicons:arrow-left-solid',
          'heroicons:device-phone-mobile',
          'heroicons:device-tablet',
          'heroicons:device-phone-mobile-solid',
          'heroicons:clock',
          'heroicons:information-circle',
          'heroicons:chevron-right',
          'heroicons:chevron-right-solid',
          'heroicons:chevron-down-20-solid',
          'heroicons:exclamation-triangle',
          'heroicons:circle-stack-solid',
          'heroicons:cpu-chip-solid',
          'heroicons:star-solid',
          'heroicons:x-circle-solid',
          'heroicons:x-mark-20-solid',
      ],
      scan: true,
      includeCustomCollections: true,
      sizeLimitKb: 256,
    },
  },
  
  // 環境變數
  runtimeConfig: {
    // 私有鍵（只在伺服器端可用）
    
    // 公開鍵（會暴露給客戶端）
    public: {
      apiBaseUrl: process.env.NUXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'
    }
  },
  
  // 自動匯入
  imports: {
    dirs: [
      'composables',
      'composables/*/index.{ts,js,mjs,mts}',
      'composables/**'
    ]
  },
  
  // TypeScript 設定
  typescript: {
    typeCheck: true
  },
  
  // 開發伺服器設定
  devServer: {
    port: 3000,
    host: 'localhost'
  },
  
  // Nitro 設定 - API 代理
  nitro: {
    devProxy: {
      '/api': {
        target: process.env.NUXT_PUBLIC_API_BASE_URL || 'http://localhost:8000',
        changeOrigin: true
      }
    }
  },
  
  // 建置設定
  build: {
    transpile: ['chart.js']
  },
  
  // 應用程式設定
  app: {
    head: {
      title: '電信門市銷售助理系統',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'description', content: 'AI 驅動的電信門市續約銷售輔助系統' }
      ],
      link: [
        { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' }
      ]
    }
  }
})