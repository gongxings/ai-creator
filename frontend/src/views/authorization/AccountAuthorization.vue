<template>
  <div class="account-authorization flagship-page page-shell">
    <section class="page-hero auth-hero">
      <div class="hero-grid">
        <div class="hero-main">
          <span class="hero-eyebrow">Authorization</span>
          <h1 class="hero-title">账号授权中心</h1>
          <p class="hero-subtitle">统一管理发布平台与AI平台的账号授权，让创作与发布更便捷。</p>
          <div class="hero-actions">
            <el-button type="primary" @click="handleAddAccount">
              <el-icon><Plus /></el-icon>
              添加账号
            </el-button>
          </div>
        </div>
        <div class="hero-panel">
          <div class="hero-panel-title">授权概览</div>
          <div class="hero-stats">
            <div class="hero-stat">
              <div class="hero-stat-value">{{ publishAccounts.length }}</div>
              <div class="hero-stat-label">发布平台</div>
            </div>
            <div class="hero-stat">
              <div class="hero-stat-value">{{ aiAccounts.length }}</div>
              <div class="hero-stat-label">AI平台</div>
            </div>
            <div class="hero-stat">
              <div class="hero-stat-value">{{ validAccountsCount }}</div>
              <div class="hero-stat-label">有效账号</div>
            </div>
            <div class="hero-stat">
              <div class="hero-stat-value">{{ expiredAccountsCount }}</div>
              <div class="hero-stat-label">需更新</div>
            </div>
          </div>
          <div class="hero-tags">
            <span class="hero-tag">Cookie授权</span>
            <span class="hero-tag">自动获取</span>
            <span class="hero-tag">统一管理</span>
          </div>
        </div>
      </div>
    </section>

    <section class="page-dashboard">
      <div class="dashboard-grid">
        <div class="dashboard-card">
          <div class="label">发布平台</div>
          <div class="value">{{ publishAccounts.length }}</div>
          <div class="delta">微信/小红书/抖音等</div>
        </div>
        <div class="dashboard-card">
          <div class="label">AI平台</div>
          <div class="value">{{ aiAccounts.length }}</div>
          <div class="delta">豆包/千问等免费额度</div>
        </div>
        <div class="dashboard-card">
          <div class="label">总账号数</div>
          <div class="value">{{ publishAccounts.length + aiAccounts.length }}</div>
          <div class="delta">统一管理更便捷</div>
        </div>
      </div>
    </section>

    <section class="page-body">
      <div class="main-panel">
        <el-card class="auth-card">
          <template #header>
            <div class="card-header">
              <el-icon><Key /></el-icon>
              <span>账号授权管理</span>
            </div>
          </template>

          <el-tabs v-model="activeTab" class="auth-tabs">
            <!-- 发布平台账号 -->
            <el-tab-pane label="发布平台账号" name="publish">
              <PublishAccountsManagement 
                ref="publishAccountsRef"
                @accounts-updated="loadPublishAccounts" 
              />
            </el-tab-pane>

            <!-- AI平台账号 -->
            <el-tab-pane label="AI平台账号" name="ai">
              <AIAccountsManagement 
                ref="aiAccountsRef"
                @accounts-updated="loadAIAccounts" 
              />
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </div>
      
      <aside class="side-panel">
        <div class="panel">
          <h3 class="panel-title">授权说明</h3>
          <p class="panel-subtitle">两种账号类型的区别</p>
          <div class="info-list">
            <div class="info-item">
              <div class="info-icon"><el-icon><Upload /></el-icon></div>
              <div>
                <div class="info-title">发布平台账号</div>
                <div class="info-desc">用于将创作内容发布到微信公众号、小红书、抖音等平台。</div>
              </div>
            </div>
            <div class="info-item">
              <div class="info-icon"><el-icon><Cpu /></el-icon></div>
              <div>
                <div class="info-title">AI平台账号</div>
                <div class="info-desc">绑定豆包、通义千问等平台，使用其免费AI额度进行创作。</div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="panel">
          <h3 class="panel-title">授权方式</h3>
          <div class="info-list">
            <div class="info-item">
              <div class="info-icon success"><el-icon><VideoCamera /></el-icon></div>
              <div>
                <div class="info-title">远程浏览器（推荐）</div>
                <div class="info-desc">实时操作，自动获取Cookie。</div>
              </div>
            </div>
            <div class="info-item">
              <div class="info-icon"><el-icon><Link /></el-icon></div>
              <div>
                <div class="info-title">前端授权</div>
                <div class="info-desc">弹窗登录，手动确认。</div>
              </div>
            </div>
            <div class="info-item">
              <div class="info-icon"><el-icon><Monitor /></el-icon></div>
              <div>
                <div class="info-title">后端授权</div>
                <div class="info-desc">系统自动打开浏览器。</div>
              </div>
            </div>
          </div>
        </div>
      </aside>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Key, Upload, Cpu, VideoCamera, Link, Monitor } from '@element-plus/icons-vue'
import PublishAccountsManagement from '@/components/PublishAccountsManagement.vue'
import AIAccountsManagement from '@/components/AIAccountsManagement.vue'
import { getPlatformAccounts } from '@/api/publish'
import { getAccounts } from '@/api/oauth'

// Tab状态
const activeTab = ref('publish')

// 组件引用
const publishAccountsRef = ref()
const aiAccountsRef = ref()

// 账号数据
const publishAccounts = ref<any[]>([])
const aiAccounts = ref<any[]>([])

// 计算属性
const validAccountsCount = computed(() => {
  const validPublish = publishAccounts.value.filter(a => a.cookies_valid === 'valid').length
  const validAI = aiAccounts.value.filter(a => a.is_active && !a.is_expired).length
  return validPublish + validAI
})

const expiredAccountsCount = computed(() => {
  const expiredPublish = publishAccounts.value.filter(a => a.cookies_valid === 'invalid').length
  const expiredAI = aiAccounts.value.filter(a => a.is_expired).length
  return expiredPublish + expiredAI
})

// 加载发布平台账号
const loadPublishAccounts = async () => {
  try {
    const response = await getPlatformAccounts()
    publishAccounts.value = response || []
  } catch (error: any) {
    console.error('加载发布平台账号失败:', error)
  }
}

// 加载AI平台账号
const loadAIAccounts = async () => {
  try {
    const response = await getAccounts()
    aiAccounts.value = response.data || []
  } catch (error: any) {
    console.error('加载AI平台账号失败:', error)
  }
}

// 添加账号
const handleAddAccount = () => {
  if (activeTab.value === 'publish') {
    publishAccountsRef.value?.openAddDialog()
  } else {
    aiAccountsRef.value?.openAddDialog()
  }
}

// 初始化
onMounted(() => {
  loadPublishAccounts()
  loadAIAccounts()
})
</script>

<style scoped lang="scss">
.account-authorization {
  padding: 20px;
  --hero-from: rgba(16, 185, 129, 0.18);
  --hero-to: rgba(59, 130, 246, 0.18);
  --page-accent: #10b981;

  .page-body {
    align-items: stretch;
  }

  .main-panel,
  .side-panel {
    height: 100%;
  }

  .auth-card {
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;

    .card-header {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 18px;
      font-weight: 600;
    }
  }

  :deep(.auth-card .el-card__body) {
    flex: 1;
    display: flex;
    flex-direction: column;
    min-height: 0;
  }

  .auth-tabs {
    margin-top: 16px;
    flex: 1;
    display: flex;
    flex-direction: column;
    min-height: 0;
  }

  :deep(.auth-tabs .el-tabs__content) {
    flex: 1;
    min-height: 0;
  }

  :deep(.auth-tabs .el-tab-pane) {
    height: 100%;
  }

  // 侧边栏图标样式
  .side-panel {
    .info-icon {
      &.success {
        background: rgba(16, 185, 129, 0.1);
        color: #10b981;
      }
    }
  }
}
</style>
