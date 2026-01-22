#!/bin/bash

# 创建前端目录结构和核心文件的脚本

# 创建目录结构
mkdir -p frontend/src/{api,components,layout,router,store,styles,types,utils,views/{auth,writing,image,video,ppt,history,publish,admin}}

# 创建 .env 文件
cat > frontend/.env.development << 'EOF'
# 开发环境配置
VITE_APP_TITLE=AI创作者平台
VITE_API_BASE_URL=/api
VITE_APP_PORT=3000
EOF

cat > frontend/.env.production << 'EOF'
# 生产环境配置
VITE_APP_TITLE=AI创作者平台
VITE_API_BASE_URL=/api
EOF

# 创建 .gitignore
cat > frontend/.gitignore << 'EOF'
node_modules
dist
dist-ssr
*.local
.vscode/*
!.vscode/extensions.json
.idea
.DS_Store
*.suo
*.ntvs*
*.njsproj
*.sln
*.sw?
EOF

# 创建 main.ts
cat > frontend/src/main.ts << 'EOF'
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import zhCn from 'element-plus/es/locale/lang/zh-cn'

import App from './App.vue'
import router from './router'
import './styles/index.scss'

const app = createApp(App)

for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(createPinia())
app.use(router)
app.use(ElementPlus, { locale: zhCn })

app.mount('#app')
EOF

# 创建 App.vue
cat > frontend/src/App.vue << 'EOF'
<template>
  <router-view />
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useUserStore } from '@/store/user'

const userStore = useUserStore()

onMounted(() => {
  userStore.restoreUser()
})
</script>

<style lang="scss">
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body, #app {
  width: 100%;
  height: 100%;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}
</style>
EOF

# 创建样式文件
cat > frontend/src/styles/index.scss << 'EOF'
$primary-color: #409eff;

.text-center { text-align: center; }
.mt-20 { margin-top: 20px; }
.mb-20 { margin-bottom: 20px; }

::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-thumb {
  background-color: #dcdfe6;
  border-radius: 4px;
}

.page-container {
  padding: 20px;
  min-height: calc(100vh - 60px);
}

.tool-card {
  cursor: pointer;
  transition: all 0.3s;
  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.15);
  }
}
EOF

echo "前端目录结构创建完成！"
echo "请运行以下命令安装依赖："
echo "cd frontend && npm install"
