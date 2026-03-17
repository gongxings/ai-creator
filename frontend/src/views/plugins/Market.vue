<template>
  <div class="plugin-market">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1>插件市场</h1>
      <p class="subtitle">发现并安装插件，增强您的创作体验</p>
    </div>

    <!-- 搜索和筛选 -->
    <div class="filter-bar">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索插件..."
        prefix-icon="Search"
        clearable
        @input="handleSearch"
        class="search-input"
      />
      <div class="category-tabs">
        <el-radio-group v-model="selectedCategory" @change="loadPlugins">
          <el-radio-button label="">全部</el-radio-button>
          <el-radio-button
            v-for="cat in categories"
            :key="cat.key"
            :label="cat.key"
          >
            {{ cat.name }} ({{ cat.count }})
          </el-radio-button>
        </el-radio-group>
      </div>
    </div>

    <!-- 插件列表 -->
    <div v-loading="loading" class="plugin-grid">
      <el-empty v-if="!loading && plugins.length === 0" description="暂无插件" />
      
      <div
        v-for="plugin in plugins"
        :key="plugin.id"
        class="plugin-card"
        @click="showPluginDetail(plugin)"
      >
        <div class="plugin-header">
          <div class="plugin-icon">
            <el-icon v-if="plugin.icon" :size="32">
              <component :is="getIconComponent(plugin.icon)" />
            </el-icon>
            <span v-else class="icon-placeholder">{{ plugin.display_name.charAt(0) }}</span>
          </div>
          <div class="plugin-info">
            <h3>{{ plugin.display_name }}</h3>
            <div class="plugin-meta">
              <el-tag v-if="plugin.is_official" type="success" size="small">官方</el-tag>
              <span class="category">{{ getCategoryName(plugin.category) }}</span>
            </div>
          </div>
        </div>
        
        <p class="plugin-desc">{{ plugin.short_description || '暂无描述' }}</p>
        
        <div class="plugin-footer">
          <div class="plugin-stats">
            <span class="stat">
              <el-icon><Download /></el-icon>
              {{ formatNumber(plugin.download_count) }}
            </span>
            <span class="stat">
              <el-icon><Star /></el-icon>
              {{ plugin.rating.toFixed(1) }}
            </span>
          </div>
          <el-button
            v-if="plugin.is_installed"
            type="success"
            size="small"
            plain
            @click.stop="goToMyPlugins"
          >
            已安装
          </el-button>
          <el-button
            v-else
            type="primary"
            size="small"
            @click.stop="handleInstall(plugin)"
          >
            安装
          </el-button>
        </div>
      </div>
    </div>

    <!-- 分页 -->
    <div v-if="total > pageSize" class="pagination">
      <el-pagination
        v-model:current-page="currentPage"
        :page-size="pageSize"
        :total="total"
        layout="prev, pager, next"
        @current-change="loadPlugins"
      />
    </div>

    <!-- 插件详情弹窗 -->
    <el-dialog
      v-model="detailDialogVisible"
      :title="currentPlugin?.display_name"
      width="600px"
      class="plugin-detail-dialog"
    >
      <div v-if="currentPlugin" class="plugin-detail">
        <div class="detail-header">
          <div class="plugin-icon large">
            <el-icon v-if="currentPlugin.icon" :size="48">
              <component :is="getIconComponent(currentPlugin.icon)" />
            </el-icon>
            <span v-else class="icon-placeholder">{{ currentPlugin.display_name.charAt(0) }}</span>
          </div>
          <div class="detail-info">
            <h2>{{ currentPlugin.display_name }}</h2>
            <div class="detail-meta">
              <el-tag v-if="currentPlugin.is_official" type="success">官方插件</el-tag>
              <span>v{{ currentPlugin.version }}</span>
              <span>作者: {{ currentPlugin.author }}</span>
            </div>
            <div class="detail-stats">
              <span><el-icon><Download /></el-icon> {{ formatNumber(currentPlugin.download_count) }} 次安装</span>
              <span><el-icon><Star /></el-icon> {{ currentPlugin.rating.toFixed(1) }} 分 ({{ currentPlugin.review_count }} 评价)</span>
            </div>
          </div>
        </div>
        
        <el-divider />
        
        <div class="detail-description">
          <h4>插件介绍</h4>
          <p>{{ currentPlugin.description || currentPlugin.short_description || '暂无介绍' }}</p>
        </div>
        
        <div v-if="currentPlugin.tags && currentPlugin.tags.length > 0" class="detail-tags">
          <h4>标签</h4>
          <el-tag v-for="tag in currentPlugin.tags" :key="tag" class="tag">{{ tag }}</el-tag>
        </div>
        
        <!-- 配置表单（如果需要） -->
        <div v-if="hasConfigSchema && !currentPlugin.is_installed" class="detail-config">
          <h4>配置</h4>
          <el-form :model="installConfig" label-width="100px">
            <el-form-item
              v-for="(prop, key) in configProperties"
              :key="key"
              :label="prop.title || key"
              :required="isRequired(key)"
            >
              <el-input
                v-if="prop.type === 'string'"
                v-model="installConfig[key]"
                :type="key.includes('key') || key.includes('secret') ? 'password' : 'text'"
                :placeholder="prop.description"
              />
            </el-form-item>
          </el-form>
        </div>
      </div>
      
      <template #footer>
        <el-button @click="detailDialogVisible = false">取消</el-button>
        <el-button
          v-if="currentPlugin && !currentPlugin.is_installed"
          type="primary"
          :loading="installing"
          @click="confirmInstall"
        >
          安装插件
        </el-button>
        <el-button
          v-else-if="currentPlugin && currentPlugin.is_installed"
          type="danger"
          @click="handleUninstall"
        >
          卸载插件
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Download, Star } from '@element-plus/icons-vue'
import * as Icons from '@element-plus/icons-vue'
import {
  getPluginMarket,
  getPluginCategories,
  getPluginDetail,
  installPlugin,
  uninstallPlugin,
  type PluginMarketItem,
  type PluginMarketDetail,
  type PluginCategory,
} from '@/api/plugins'

const router = useRouter()

// 状态
const loading = ref(false)
const plugins = ref<PluginMarketItem[]>([])
const categories = ref<PluginCategory[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = 12
const searchKeyword = ref('')
const selectedCategory = ref('')

// 详情弹窗
const detailDialogVisible = ref(false)
const currentPlugin = ref<PluginMarketDetail | null>(null)
const installConfig = ref<Record<string, any>>({})
const installing = ref(false)

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
  const cat = categories.value.find(c => c.key === key)
  return cat?.name || key
}

const getIconComponent = (iconName: string) => {
  return (Icons as any)[iconName] || Icons.Document
}

const formatNumber = (num: number) => {
  if (num >= 10000) return (num / 10000).toFixed(1) + 'w'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'k'
  return num.toString()
}

const isRequired = (key: string) => {
  const required = currentPlugin.value?.config_schema?.required || []
  return required.includes(key)
}

const loadCategories = async () => {
  try {
    const res = await getPluginCategories()
    categories.value = res.data || []
  } catch (e) {
    console.error('Failed to load categories:', e)
  }
}

const loadPlugins = async () => {
  loading.value = true
  try {
    const res = await getPluginMarket({
      category: selectedCategory.value || undefined,
      search: searchKeyword.value || undefined,
      skip: (currentPage.value - 1) * pageSize,
      limit: pageSize,
    })
    plugins.value = res.data?.items || []
    total.value = res.data?.total || 0
  } catch (e) {
    console.error('Failed to load plugins:', e)
    ElMessage.error('加载插件列表失败')
  } finally {
    loading.value = false
  }
}

let searchTimeout: number
const handleSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = window.setTimeout(() => {
    currentPage.value = 1
    loadPlugins()
  }, 300)
}

const showPluginDetail = async (plugin: PluginMarketItem) => {
  try {
    const res = await getPluginDetail(plugin.name)
    currentPlugin.value = res.data
    installConfig.value = {}
    detailDialogVisible.value = true
  } catch (e) {
    ElMessage.error('加载插件详情失败')
  }
}

const handleInstall = (plugin: PluginMarketItem) => {
  showPluginDetail(plugin)
}

const confirmInstall = async () => {
  if (!currentPlugin.value) return
  
  // 验证必填配置
  const required = currentPlugin.value.config_schema?.required || []
  for (const key of required) {
    if (!installConfig.value[key]) {
      ElMessage.warning(`请填写 ${configProperties.value[key]?.title || key}`)
      return
    }
  }
  
  installing.value = true
  try {
    await installPlugin({
      plugin_name: currentPlugin.value.name,
      config: installConfig.value,
    })
    ElMessage.success('插件安装成功')
    detailDialogVisible.value = false
    loadPlugins()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '安装失败')
  } finally {
    installing.value = false
  }
}

const handleUninstall = async () => {
  if (!currentPlugin.value) return
  
  try {
    await ElMessageBox.confirm(
      `确定要卸载插件「${currentPlugin.value.display_name}」吗？`,
      '确认卸载',
      { type: 'warning' }
    )
    
    await uninstallPlugin(currentPlugin.value.name)
    ElMessage.success('插件已卸载')
    detailDialogVisible.value = false
    loadPlugins()
  } catch (e: any) {
    if (e !== 'cancel') {
      ElMessage.error(e.response?.data?.detail || '卸载失败')
    }
  }
}

const goToMyPlugins = () => {
  router.push('/plugins/my-plugins')
}

// 初始化
onMounted(() => {
  loadCategories()
  loadPlugins()
})
</script>

<style scoped lang="scss">
.plugin-market {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 24px;
  
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

.filter-bar {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
  flex-wrap: wrap;
  
  .search-input {
    width: 300px;
  }
  
  .category-tabs {
    flex: 1;
  }
}

.plugin-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  min-height: 200px;
}

.plugin-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s;
  border: 1px solid #eee;
  
  &:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    transform: translateY(-2px);
  }
  
  .plugin-header {
    display: flex;
    gap: 12px;
    margin-bottom: 12px;
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
    
    .icon-placeholder {
      font-size: 20px;
      font-weight: 600;
    }
  }
  
  .plugin-info {
    flex: 1;
    
    h3 {
      margin: 0 0 4px;
      font-size: 16px;
      font-weight: 600;
    }
    
    .plugin-meta {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 12px;
      color: #999;
    }
  }
  
  .plugin-desc {
    color: #666;
    font-size: 14px;
    line-height: 1.5;
    margin: 0 0 16px;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
  
  .plugin-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    .plugin-stats {
      display: flex;
      gap: 16px;
      
      .stat {
        display: flex;
        align-items: center;
        gap: 4px;
        color: #999;
        font-size: 13px;
      }
    }
  }
}

.pagination {
  margin-top: 24px;
  display: flex;
  justify-content: center;
}

// 详情弹窗样式
.plugin-detail {
  .detail-header {
    display: flex;
    gap: 20px;
    
    .plugin-icon.large {
      width: 72px;
      height: 72px;
      border-radius: 16px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      display: flex;
      align-items: center;
      justify-content: center;
      color: #fff;
      flex-shrink: 0;
      
      .icon-placeholder {
        font-size: 28px;
        font-weight: 600;
      }
    }
    
    .detail-info {
      h2 {
        margin: 0 0 8px;
        font-size: 20px;
      }
      
      .detail-meta {
        display: flex;
        gap: 12px;
        align-items: center;
        color: #666;
        font-size: 13px;
        margin-bottom: 8px;
      }
      
      .detail-stats {
        display: flex;
        gap: 20px;
        color: #999;
        font-size: 13px;
        
        span {
          display: flex;
          align-items: center;
          gap: 4px;
        }
      }
    }
  }
  
  .detail-description {
    h4 {
      margin: 0 0 8px;
      font-size: 14px;
      color: #333;
    }
    
    p {
      color: #666;
      line-height: 1.6;
      white-space: pre-wrap;
    }
  }
  
  .detail-tags {
    margin-top: 16px;
    
    h4 {
      margin: 0 0 8px;
      font-size: 14px;
      color: #333;
    }
    
    .tag {
      margin-right: 8px;
      margin-bottom: 8px;
    }
  }
  
  .detail-config {
    margin-top: 16px;
    padding: 16px;
    background: #f9f9f9;
    border-radius: 8px;
    
    h4 {
      margin: 0 0 12px;
      font-size: 14px;
      color: #333;
    }
  }
}
</style>
