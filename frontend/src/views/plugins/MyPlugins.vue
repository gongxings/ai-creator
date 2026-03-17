<template>
  <div class="my-plugins">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1>我的插件</h1>
        <p class="subtitle">管理已安装的插件</p>
      </div>
      <el-button type="primary" @click="goToMarket">
        <el-icon><Plus /></el-icon>
        浏览插件市场
      </el-button>
    </div>

    <!-- 插件列表 -->
    <div v-loading="loading" class="plugins-container">
      <el-empty v-if="!loading && plugins.length === 0" description="您还没有安装任何插件">
        <el-button type="primary" @click="goToMarket">去插件市场看看</el-button>
      </el-empty>
      
      <div v-else class="plugin-list">
        <div
          v-for="plugin in plugins"
          :key="plugin.id"
          class="plugin-item"
        >
          <div class="plugin-main">
            <div class="plugin-icon">
              <el-icon v-if="plugin.icon" :size="32">
                <component :is="getIconComponent(plugin.icon)" />
              </el-icon>
              <span v-else class="icon-placeholder">{{ plugin.display_name.charAt(0) }}</span>
            </div>
            
            <div class="plugin-info">
              <h3>{{ plugin.display_name }}</h3>
              <div class="plugin-meta">
                <span class="category">{{ getCategoryName(plugin.category) }}</span>
                <span v-if="plugin.usage_count > 0" class="usage">
                  已使用 {{ plugin.usage_count }} 次
                </span>
                <span v-if="plugin.last_used_at" class="last-used">
                  上次使用: {{ formatDate(plugin.last_used_at) }}
                </span>
              </div>
            </div>
          </div>
          
          <div class="plugin-actions">
            <el-switch
              v-model="plugin.is_enabled"
              active-text="启用"
              inactive-text="禁用"
              @change="handleToggle(plugin)"
            />
            
            <el-tooltip content="自动使用" placement="top">
              <el-checkbox
                v-model="plugin.is_auto_use"
                label="自动"
                @change="handleAutoUseChange(plugin)"
              />
            </el-tooltip>
            
            <el-button
              size="small"
              @click="showConfigDialog(plugin)"
            >
              配置
            </el-button>
            
            <el-button
              type="danger"
              size="small"
              plain
              @click="handleUninstall(plugin)"
            >
              卸载
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 使用统计 -->
    <div v-if="stats.length > 0" class="stats-section">
      <h2>使用统计</h2>
      <el-table :data="stats" stripe>
        <el-table-column prop="display_name" label="插件" width="200" />
        <el-table-column prop="total_calls" label="总调用" width="100" />
        <el-table-column prop="success_calls" label="成功" width="100" />
        <el-table-column prop="failed_calls" label="失败" width="100" />
        <el-table-column label="平均耗时" width="120">
          <template #default="{ row }">
            {{ row.avg_duration_ms ? row.avg_duration_ms.toFixed(0) + 'ms' : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="最后使用" width="180">
          <template #default="{ row }">
            {{ row.last_used_at ? formatDate(row.last_used_at) : '-' }}
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 配置弹窗 -->
    <el-dialog
      v-model="configDialogVisible"
      :title="`配置 - ${currentPlugin?.display_name}`"
      width="500px"
    >
      <div v-if="currentPlugin">
        <el-form v-if="hasConfigSchema" :model="editingConfig" label-width="100px">
          <el-form-item
            v-for="(prop, key) in configProperties"
            :key="key"
            :label="prop.title || key"
          >
            <el-input
              v-if="prop.type === 'string'"
              v-model="editingConfig[key]"
              :type="key.includes('key') || key.includes('secret') ? 'password' : 'text'"
              :placeholder="prop.description"
              show-password
            />
          </el-form-item>
        </el-form>
        <el-empty v-else description="此插件无需配置" />
      </div>
      
      <template #footer>
        <el-button @click="configDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveConfig" :loading="saving">
          保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import * as Icons from '@element-plus/icons-vue'
import {
  getMyPlugins,
  getMyPluginDetail,
  updateMyPlugin,
  uninstallPlugin,
  getPluginStats,
  type UserPluginItem,
  type UserPluginDetail,
  type PluginStats,
} from '@/api/plugins'

const router = useRouter()

// 状态
const loading = ref(false)
const plugins = ref<(UserPluginItem & { is_enabled: boolean; is_auto_use: boolean })[]>([])
const stats = ref<PluginStats[]>([])

// 配置弹窗
const configDialogVisible = ref(false)
const currentPlugin = ref<UserPluginDetail | null>(null)
const editingConfig = ref<Record<string, any>>({})
const saving = ref(false)

// 分类映射
const categoryMap: Record<string, string> = {
  search: '搜索工具',
  writing: '写作辅助',
  media: '媒体处理',
  utility: '实用工具',
}

// 计算属性
const hasConfigSchema = computed(() => {
  if (!currentPlugin.value?.config_schema) return false
  const schema = currentPlugin.value.config_schema
  return schema.properties && Object.keys(schema.properties).length > 0
})

const configProperties = computed(() => {
  return currentPlugin.value?.config_schema?.properties || {}
})

// 方法
const getCategoryName = (key: string) => {
  return categoryMap[key] || key
}

const getIconComponent = (iconName: string) => {
  return (Icons as any)[iconName] || Icons.Document
}

const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const loadPlugins = async () => {
  loading.value = true
  try {
    const res = await getMyPlugins()
    plugins.value = (res.data || []).map(p => ({
      ...p,
      is_enabled: p.is_enabled,
      is_auto_use: p.is_auto_use,
    }))
  } catch (e) {
    ElMessage.error('加载插件列表失败')
  } finally {
    loading.value = false
  }
}

const loadStats = async () => {
  try {
    const res = await getPluginStats()
    stats.value = res.data || []
  } catch (e) {
    console.error('Failed to load stats:', e)
  }
}

const handleToggle = async (plugin: UserPluginItem & { is_enabled: boolean }) => {
  try {
    await updateMyPlugin(plugin.plugin_name, { is_enabled: plugin.is_enabled })
    ElMessage.success(plugin.is_enabled ? '插件已启用' : '插件已禁用')
  } catch (e) {
    // 恢复状态
    plugin.is_enabled = !plugin.is_enabled
    ElMessage.error('操作失败')
  }
}

const handleAutoUseChange = async (plugin: UserPluginItem & { is_auto_use: boolean }) => {
  try {
    await updateMyPlugin(plugin.plugin_name, { is_auto_use: plugin.is_auto_use })
    ElMessage.success(plugin.is_auto_use ? '已开启自动使用' : '已关闭自动使用')
  } catch (e) {
    // 恢复状态
    plugin.is_auto_use = !plugin.is_auto_use
    ElMessage.error('操作失败')
  }
}

const showConfigDialog = async (plugin: UserPluginItem) => {
  try {
    const res = await getMyPluginDetail(plugin.plugin_name)
    currentPlugin.value = res.data
    editingConfig.value = { ...(res.data?.config || {}) }
    configDialogVisible.value = true
  } catch (e) {
    ElMessage.error('加载插件配置失败')
  }
}

const saveConfig = async () => {
  if (!currentPlugin.value) return
  
  saving.value = true
  try {
    await updateMyPlugin(currentPlugin.value.plugin_name, { config: editingConfig.value })
    ElMessage.success('配置已保存')
    configDialogVisible.value = false
    loadPlugins()
  } catch (e) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

const handleUninstall = async (plugin: UserPluginItem) => {
  try {
    await ElMessageBox.confirm(
      `确定要卸载插件「${plugin.display_name}」吗？卸载后配置将丢失。`,
      '确认卸载',
      { type: 'warning' }
    )
    
    await uninstallPlugin(plugin.plugin_name)
    ElMessage.success('插件已卸载')
    loadPlugins()
    loadStats()
  } catch (e: any) {
    if (e !== 'cancel') {
      ElMessage.error('卸载失败')
    }
  }
}

const goToMarket = () => {
  router.push('/plugins/market')
}

// 初始化
onMounted(() => {
  loadPlugins()
  loadStats()
})
</script>

<style scoped lang="scss">
.my-plugins {
  padding: 24px;
  max-width: 1000px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  
  .header-left {
    h1 {
      font-size: 28px;
      font-weight: 600;
      margin: 0 0 8px;
    }
    
    .subtitle {
      color: #666;
      margin: 0;
    }
  }
}

.plugins-container {
  min-height: 200px;
}

.plugin-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.plugin-item {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
  
  .plugin-main {
    display: flex;
    gap: 16px;
    align-items: center;
  }
  
  .plugin-icon {
    width: 48px;
    height: 48px;
    border-radius: 10px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    flex-shrink: 0;
    
    .icon-placeholder {
      font-size: 20px;
      font-weight: 600;
    }
  }
  
  .plugin-info {
    h3 {
      margin: 0 0 4px;
      font-size: 16px;
      font-weight: 600;
    }
    
    .plugin-meta {
      display: flex;
      gap: 12px;
      font-size: 13px;
      color: #999;
      
      .category {
        color: #666;
      }
    }
  }
  
  .plugin-actions {
    display: flex;
    align-items: center;
    gap: 16px;
  }
}

.stats-section {
  margin-top: 40px;
  
  h2 {
    font-size: 18px;
    font-weight: 600;
    margin-bottom: 16px;
  }
}
</style>
