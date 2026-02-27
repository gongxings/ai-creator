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
              <el-tag v-if="model.is_preferred" type="primary" size="small" effect="plain">常用</el-tag>
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

watch(
  () => props.modelValue,
  (newValue) => {
    if (newValue !== selectedModel.value) {
      selectedModel.value = newValue || ''
    }
  }
)

const groupedModels = computed(() => {
  const apiKeyModels = models.value.filter((m) => m.source_type === 'api_key')
  const groups: Array<{ label: string; models: AvailableModel[] }> = []
  if (apiKeyModels.length > 0) {
    groups.push({ label: 'API Key 模型', models: apiKeyModels })
  }
  return groups
})

const loadModels = async () => {
  loading.value = true
  try {
    const response = await getAvailableModels(props.sceneType)
    models.value = response.models

    if (!selectedModel.value) {
      const preferredModel = models.value.find((m) => m.is_preferred && m.status === 'active')
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

const handleModelChange = (modelId: string) => {
  const model = models.value.find((m) => m.model_id === modelId)
  emit('update:modelValue', modelId)
  emit('change', model)
}

const refresh = () => {
  loadModels()
}

onMounted(() => {
  loadModels()
})

defineExpose({ refresh })
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
}
</style>
