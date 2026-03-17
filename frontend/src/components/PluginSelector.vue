<template>
  <div class="plugin-selector">
    <!-- 触发按钮 -->
    <el-popover
      :visible="popoverVisible"
      placement="bottom-start"
      :width="360"
      trigger="click"
      @update:visible="popoverVisible = $event"
    >
      <template #reference>
        <el-button :type="hasSelection ? 'primary' : 'default'" plain>
          <el-icon><Connection /></el-icon>
          插件
          <el-badge v-if="selectedCount > 0" :value="selectedCount" class="plugin-badge" />
        </el-button>
      </template>
      
      <div class="plugin-popover">
        <div class="popover-header">
          <span class="title">选择创作插件</span>
          <el-button link type="primary" size="small" @click="goToMarket">
            管理插件
          </el-button>
        </div>
        
        <div v-if="loading" class="loading-state">
          <el-icon class="is-loading"><Loading /></el-icon>
          <span>加载中...</span>
        </div>
        
        <div v-else-if="plugins.length === 0" class="empty-state">
          <p>您还没有安装任何插件</p>
          <el-button type="primary" size="small" @click="goToMarket">
            去插件市场
          </el-button>
        </div>
        
        <div v-else class="plugin-list">
          <div
            v-for="plugin in plugins"
            :key="plugin.name"
            class="plugin-item"
            :class="{ selected: isSelected(plugin.name), disabled: !plugin.is_enabled }"
            @click="togglePlugin(plugin)"
          >
            <el-checkbox
              :model-value="isSelected(plugin.name)"
              :disabled="!plugin.is_enabled"
              @click.stop
              @change="togglePlugin(plugin)"
            />
            <div class="plugin-info">
              <div class="plugin-name">
                {{ plugin.display_name }}
                <el-tag v-if="!plugin.is_enabled" size="small" type="info">已禁用</el-tag>
              </div>
              <div class="plugin-desc">{{ truncate(plugin.description, 50) }}</div>
            </div>
          </div>
        </div>
        
        <div class="popover-footer">
          <el-checkbox
            v-model="rememberSelection"
            label="记住选择"
            size="small"
          />
          <el-button type="primary" size="small" @click="confirmSelection">
            确定
          </el-button>
        </div>
      </div>
    </el-popover>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Connection, Loading } from '@element-plus/icons-vue'
import {
  getPluginsForCreation,
  savePluginSelection,
  type PluginForCreation,
} from '@/api/plugins'

const props = defineProps<{
  toolType: string
  modelValue?: string[]
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string[]): void
  (e: 'change', value: string[]): void
}>()

const router = useRouter()

// 状态
const loading = ref(false)
const popoverVisible = ref(false)
const plugins = ref<PluginForCreation[]>([])
const selectedPlugins = ref<string[]>([])
const rememberSelection = ref(true)

// 计算属性
const selectedCount = computed(() => selectedPlugins.value.length)
const hasSelection = computed(() => selectedCount.value > 0)

// 方法
const truncate = (text: string, maxLength: number) => {
  if (!text) return ''
  if (text.length <= maxLength) return text
  return text.slice(0, maxLength) + '...'
}

const isSelected = (name: string) => {
  return selectedPlugins.value.includes(name)
}

const togglePlugin = (plugin: PluginForCreation) => {
  if (!plugin.is_enabled) return
  
  const index = selectedPlugins.value.indexOf(plugin.name)
  if (index > -1) {
    selectedPlugins.value.splice(index, 1)
  } else {
    selectedPlugins.value.push(plugin.name)
  }
}

const loadPlugins = async () => {
  if (!props.toolType) return
  
  loading.value = true
  try {
    const res = await getPluginsForCreation(props.toolType)
    plugins.value = res.data?.plugins || []
    
    // 初始化选择状态
    selectedPlugins.value = plugins.value
      .filter(p => p.is_selected && p.is_enabled)
      .map(p => p.name)
    
    // 同步到父组件
    emit('update:modelValue', selectedPlugins.value)
  } catch (e) {
    console.error('Failed to load plugins:', e)
  } finally {
    loading.value = false
  }
}

const confirmSelection = async () => {
  // 保存选择
  if (rememberSelection.value && props.toolType) {
    try {
      await savePluginSelection({
        tool_type: props.toolType,
        selected_plugins: selectedPlugins.value,
      })
    } catch (e) {
      console.error('Failed to save selection:', e)
    }
  }
  
  // 同步到父组件
  emit('update:modelValue', selectedPlugins.value)
  emit('change', selectedPlugins.value)
  
  popoverVisible.value = false
}

const goToMarket = () => {
  router.push('/plugins/my-plugins')
}

// 监听 toolType 变化
watch(() => props.toolType, () => {
  loadPlugins()
}, { immediate: true })

// 监听父组件传入的值
watch(() => props.modelValue, (val) => {
  if (val && JSON.stringify(val) !== JSON.stringify(selectedPlugins.value)) {
    selectedPlugins.value = [...val]
  }
})

// 初始化
onMounted(() => {
  loadPlugins()
})
</script>

<style scoped lang="scss">
.plugin-selector {
  display: inline-block;
  
  .plugin-badge {
    margin-left: 6px;
  }
}

.plugin-popover {
  .popover-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-bottom: 12px;
    border-bottom: 1px solid #eee;
    margin-bottom: 12px;
    
    .title {
      font-weight: 600;
      color: #333;
    }
  }
  
  .loading-state,
  .empty-state {
    text-align: center;
    padding: 24px 0;
    color: #999;
    
    .el-icon {
      font-size: 24px;
      margin-bottom: 8px;
    }
    
    p {
      margin: 0 0 12px;
    }
  }
  
  .plugin-list {
    max-height: 280px;
    overflow-y: auto;
  }
  
  .plugin-item {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 10px;
    border-radius: 8px;
    cursor: pointer;
    transition: background-color 0.2s;
    
    &:hover:not(.disabled) {
      background: #f5f7fa;
    }
    
    &.selected {
      background: #ecf5ff;
    }
    
    &.disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
    
    .plugin-info {
      flex: 1;
      min-width: 0;
      
      .plugin-name {
        font-size: 14px;
        font-weight: 500;
        color: #333;
        display: flex;
        align-items: center;
        gap: 6px;
      }
      
      .plugin-desc {
        font-size: 12px;
        color: #999;
        margin-top: 2px;
        line-height: 1.4;
      }
    }
  }
  
  .popover-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-top: 12px;
    border-top: 1px solid #eee;
    margin-top: 12px;
  }
}
</style>
