<template>
  <div class="model-selector">
    <el-select
      v-model="selectedModel"
      placeholder="选择AI模型"
      filterable
      :loading="loading"
      @change="handleModelChange"
    >
      <el-option-group
        v-for="group in groupedModels"
        :key="group.label"
        :label="group.label"
      >
        <el-option
          v-for="model in group.models"
          :key="model.model_id"
          :label="model.display_name"
          :value="model.model_id"
          :disabled="model.status !== 'active'"
        >
          <div class="model-option">
            <div class="model-info">
              <span class="model-name">{{ model.display_name }}</span>
              <el-tag
                v-if="model.is_free"
                type="success"
                size="small"
                effect="plain"
              >
                免费
              </el-tag>
              <el-tag
                v-if="model.is_preferred"
                type="primary"
                size="small"
                effect="plain"
              >
                常用
              </el-tag>
              <el-tag
                v-if="model.status === 'expired'"
                type="warning"
                size="small"
              >
                已过期
              </el-tag>
              <el-tag
                v-if="model.status === 'quota_exceeded'"
                type="danger"
                size="small"
              >
                配额用尽
              </el-tag>
            </div>
            <div v-if="model.quota_info" class="quota-info">
              <el-progress
                :percentage="model.quota_info.percentage"
                :status="getQuotaStatus(model.quota_info.percentage)"
                :show-text="false"
                :stroke-width="4"
              />
              <span class="quota-text">
                {{ formatQuota(model.quota_info.used) }} / {{ formatQuota(model.quota_info.total) }}
              </span>
            </div>
          </div>
        </el-option>
      </el-option-group>
    </el-select>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { getAvailableModels } from '@/api/models'
import type { AvailableModel } from '@/types'

interface Props {
  sceneType?: string
  modelValue?: string
}

interface Emits {
  (e: 'update:modelValue', value: string): void
  (e: 'change', model: AvailableModel | undefined): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const loading = ref(false)
const models = ref<AvailableModel[]>([])
const selectedModel = ref<string>(props.modelValue || '')

// 监听外部值变化
watch(() => props.modelValue, (newValue) => {
  if (newValue !== selectedModel.value) {
    selectedModel.value = newValue || ''
  }
})

// 分组模型
const groupedModels = computed(() => {
  const oauthModels = models.value.filter(m => m.source_type === 'oauth')
  const apiKeyModels = models.value.filter(m => m.source_type === 'api_key')
  
  const groups = []
  
  if (oauthModels.length > 0) {
    groups.push({
      label: 'OAuth账号（免费）',
      models: oauthModels
    })
  }
  
  if (apiKeyModels.length > 0) {
    groups.push({
      label: 'API Key模型',
      models: apiKeyModels
    })
  }
  
  return groups
})

// 加载模型列表
const loadModels = async () => {
  loading.value = true
  try {
    const response = await getAvailableModels(props.sceneType)
    models.value = response.models
    
    // 如果没有选中模型，自动选择偏好模型
    if (!selectedModel.value) {
      const preferredModel = models.value.find(m => m.is_preferred && m.status === 'active')
      if (preferredModel) {
        selectedModel.value = preferredModel.model_id
        emit('update:modelValue', preferredModel.model_id)
        emit('change', preferredModel)
      }
    }
  } catch (error: any) {
    ElMessage.error(error.message || '加载模型列表失败')
  } finally {
    loading.value = false
  }
}

// 处理模型变化
const handleModelChange = (modelId: string) => {
  const model = models.value.find(m => m.model_id === modelId)
  emit('update:modelValue', modelId)
  emit('change', model)
}

// 获取配额状态
const getQuotaStatus = (percentage: number) => {
  if (percentage >= 90) return 'exception'
  if (percentage >= 70) return 'warning'
  return 'success'
}

// 格式化配额
const formatQuota = (value: number) => {
  if (value >= 1000000) {
    return `${(value / 1000000).toFixed(1)}M`
  }
  if (value >= 1000) {
    return `${(value / 1000).toFixed(1)}K`
  }
  return value.toString()
}

// 刷新模型列表
const refresh = () => {
  loadModels()
}

onMounted(() => {
  loadModels()
})

// 暴露方法给父组件
defineExpose({
  refresh
})
</script>

<style scoped lang="scss">
.model-selector {
  width: 100%;
  
  :deep(.el-select) {
    width: 100%;
  }
}

.model-option {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 4px 0;
  
  .model-info {
    display: flex;
    align-items: center;
    gap: 8px;
    
    .model-name {
      flex: 1;
      font-size: 14px;
    }
  }
  
  .quota-info {
    display: flex;
    align-items: center;
    gap: 8px;
    
    :deep(.el-progress) {
      flex: 1;
    }
    
    .quota-text {
      font-size: 12px;
      color: #909399;
      white-space: nowrap;
    }
  }
}
</style>
