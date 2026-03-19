<template>
  <div class="dynamic-tool-form">
    <el-form
      ref="formRef"
      :model="formData"
      :rules="formRules"
      label-position="top"
      @submit.prevent
    >
      <el-form-item
        v-for="field in formConfig?.fields || []"
        :key="field.name"
        :label="field.label"
        :prop="field.name"
        :required="field.required"
      >
        <!-- 单行输入框 -->
        <el-input
          v-if="field.type === 'input'"
          v-model="formData[field.name]"
          :placeholder="field.placeholder"
          :maxlength="field.maxLength"
          show-word-limit
          clearable
        />

        <!-- 多行文本框 -->
        <el-input
          v-else-if="field.type === 'textarea'"
          v-model="formData[field.name]"
          type="textarea"
          :rows="field.rows || 3"
          :placeholder="field.placeholder"
          :maxlength="field.maxLength"
          show-word-limit
        />

        <!-- 下拉选择框 -->
        <el-select
          v-else-if="field.type === 'select'"
          v-model="formData[field.name]"
          :placeholder="field.placeholder || '请选择'"
          style="width: 100%"
        >
          <el-option
            v-for="option in field.options"
            :key="option.value"
            :label="option.label"
            :value="option.value"
          />
        </el-select>

        <!-- 单选框组 -->
        <el-radio-group
          v-else-if="field.type === 'radio'"
          v-model="formData[field.name]"
        >
          <el-radio
            v-for="option in field.options"
            :key="option.value"
            :label="option.value"
          >
            {{ option.label }}
          </el-radio>
        </el-radio-group>

        <!-- 数字输入框 -->
        <el-input-number
          v-else-if="field.type === 'number'"
          v-model="formData[field.name]"
          :placeholder="field.placeholder"
          style="width: 100%"
        />

        <!-- 滑块 -->
        <el-slider
          v-else-if="field.type === 'slider'"
          v-model="formData[field.name]"
          :min="field.sliderConfig?.min || 0"
          :max="field.sliderConfig?.max || 100"
          :step="field.sliderConfig?.step || 1"
          :marks="field.sliderConfig?.marks"
          :show-input="false"
        />

        <!-- 历史记录选择器 -->
        <div v-else-if="field.type === 'history_select'" class="special-field-wrapper">
          <el-select
            v-model="formData[field.name]"
            :placeholder="field.placeholder || '选择历史记录（可选）'"
            style="width: 100%"
            clearable
            filterable
            :loading="historyLoading"
            @change="(val: any) => handleHistorySelect(field, val)"
            @visible-change="(visible: boolean) => visible && loadHistoryIfNeeded()"
          >
            <el-option
              v-for="item in historyList"
              :key="item.id"
              :label="formatHistoryLabel(item)"
              :value="item.id"
            >
              <div class="history-option">
                <span class="option-title">{{ item.title || '无标题' }}</span>
                <span class="option-meta">
                  {{ toolTypeLabels[item.tool_type] || item.tool_type }} · {{ formatDate(item.created_at) }}
                </span>
              </div>
            </el-option>
          </el-select>
          <div v-if="selectedHistoryContent" class="content-preview">
            <div class="preview-header">
              <span>已选内容预览：</span>
              <el-button type="primary" link size="small" @click="clearHistorySelection(field)">
                清除选择
              </el-button>
            </div>
            <div class="preview-content">{{ selectedHistoryContent.substring(0, 200) }}{{ selectedHistoryContent.length > 200 ? '...' : '' }}</div>
          </div>
        </div>

        <!-- URL抓取输入框 -->
        <div v-else-if="field.type === 'url_fetch'" class="special-field-wrapper">
          <div class="url-fetch-input">
            <el-input
              v-model="formData[field.name]"
              :placeholder="field.placeholder || '输入网页URL'"
              clearable
              @keyup.enter="handleUrlFetch(field)"
            >
              <template #append>
                <el-button 
                  :loading="urlFetching" 
                  @click="handleUrlFetch(field)"
                  :disabled="!formData[field.name]"
                >
                  抓取内容
                </el-button>
              </template>
            </el-input>
          </div>
          <div v-if="urlFetchError" class="fetch-error">
            <el-alert :title="urlFetchError" type="error" show-icon :closable="false" />
          </div>
          <div v-if="fetchedUrlContent" class="content-preview">
            <div class="preview-header">
              <span>{{ fetchedUrlTitle ? `已抓取: ${fetchedUrlTitle}` : '已抓取内容预览：' }}</span>
              <el-button type="primary" link size="small" @click="clearUrlFetch(field)">
                清除
              </el-button>
            </div>
            <div class="preview-content">{{ fetchedUrlContent.substring(0, 300) }}{{ fetchedUrlContent.length > 300 ? '...' : '' }}</div>
          </div>
        </div>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage } from 'element-plus'
import { getToolFormConfig, toolTypeLabels } from '@/config/writingToolForms'
import { getCreations, getCreation, fetchUrlContent } from '@/api/creations'
import type { ToolFormConfig, FormField, Creation } from '@/types'

interface Props {
  toolType: string
  modelValue?: Record<string, any>
}

interface Emits {
  (e: 'update:modelValue', value: Record<string, any>): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const formRef = ref<FormInstance>()
const formData = ref<Record<string, any>>({})

// 历史记录相关
const historyList = ref<Creation[]>([])
const historyLoading = ref(false)
const historyLoaded = ref(false)
const selectedHistoryContent = ref('')

// URL抓取相关
const urlFetching = ref(false)
const urlFetchError = ref('')
const fetchedUrlContent = ref('')
const fetchedUrlTitle = ref('')

// 获取表单配置
const formConfig = computed<ToolFormConfig | undefined>(() => {
  return getToolFormConfig(props.toolType)
})

// 动态生成表单校验规则
const formRules = computed<FormRules>(() => {
  const rules: FormRules = {}
  if (!formConfig.value) return rules

  for (const field of formConfig.value.fields) {
    if (field.required) {
      rules[field.name] = [
        {
          required: true,
          message: `请输入${field.label}`,
          trigger: field.type === 'select' ? 'change' : 'blur',
        },
      ]
    }
  }
  return rules
})

// ============================================================================
// 历史记录选择相关
// ============================================================================

const loadHistoryIfNeeded = async () => {
  if (historyLoaded.value || historyLoading.value) return
  
  historyLoading.value = true
  try {
    const res = await getCreations({
      page: 1,
      page_size: 50,
      status: 'completed'
    })
    historyList.value = res.data.items || []
    historyLoaded.value = true
  } catch (error) {
    console.error('Failed to load history:', error)
  } finally {
    historyLoading.value = false
  }
}

const handleHistorySelect = async (field: FormField, creationId: number | null) => {
  if (!creationId || !field.historyConfig) {
    selectedHistoryContent.value = ''
    return
  }
  
  try {
    const res = await getCreation(creationId)
    const creation = res.data
    const content = creation.output_content || creation.content || ''
    selectedHistoryContent.value = content
    
    // 填充到目标字段
    const targetField = field.historyConfig.contentField
    if (targetField && formData.value.hasOwnProperty(targetField)) {
      formData.value[targetField] = content
    }
  } catch (error) {
    console.error('Failed to load creation detail:', error)
  }
}

const clearHistorySelection = (field: FormField) => {
  formData.value[field.name] = ''
  selectedHistoryContent.value = ''
  if (field.historyConfig?.contentField) {
    formData.value[field.historyConfig.contentField] = ''
  }
}

const formatHistoryLabel = (item: Creation): string => {
  const title = item.title || '无标题'
  const type = toolTypeLabels[item.tool_type] || item.tool_type
  return `${title} (${type})`
}

const formatDate = (dateStr: string): string => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// ============================================================================
// URL抓取相关
// ============================================================================

const handleUrlFetch = async (field: FormField) => {
  const url = formData.value[field.name]?.trim()
  if (!url) {
    ElMessage.warning('请输入URL')
    return
  }
  
  urlFetching.value = true
  urlFetchError.value = ''
  fetchedUrlContent.value = ''
  fetchedUrlTitle.value = ''
  
  try {
    const res = await fetchUrlContent(url)
    const data = res.data
    
    if (data.success) {
      fetchedUrlContent.value = data.content
      fetchedUrlTitle.value = data.title
      
      // 填充到目标字段
      const targetField = field.urlFetchConfig?.contentField
      if (targetField && formData.value.hasOwnProperty(targetField)) {
        formData.value[targetField] = data.content
      }
      
      ElMessage.success('内容抓取成功')
    } else {
      urlFetchError.value = data.error || '抓取失败'
    }
  } catch (error: any) {
    urlFetchError.value = error.message || '网络请求失败'
  } finally {
    urlFetching.value = false
  }
}

const clearUrlFetch = (field: FormField) => {
  formData.value[field.name] = ''
  fetchedUrlContent.value = ''
  fetchedUrlTitle.value = ''
  urlFetchError.value = ''
  if (field.urlFetchConfig?.contentField) {
    formData.value[field.urlFetchConfig.contentField] = ''
  }
}

// ============================================================================
// 表单数据管理
// ============================================================================

const initFormData = () => {
  const data: Record<string, any> = {}
  if (formConfig.value) {
    for (const field of formConfig.value.fields) {
      if (props.modelValue && props.modelValue[field.name] !== undefined) {
        data[field.name] = props.modelValue[field.name]
      } else if (field.defaultValue !== undefined) {
        data[field.name] = field.defaultValue
      } else {
        data[field.name] = ''
      }
    }
  }
  formData.value = data
  // 重置选择状态
  selectedHistoryContent.value = ''
  fetchedUrlContent.value = ''
  fetchedUrlTitle.value = ''
  urlFetchError.value = ''
}

watch(
  () => props.toolType,
  () => {
    initFormData()
    historyLoaded.value = false
  },
  { immediate: true }
)

watch(
  () => props.modelValue,
  (newValue) => {
    if (newValue) {
      for (const key of Object.keys(newValue)) {
        if (formData.value.hasOwnProperty(key)) {
          formData.value[key] = newValue[key]
        }
      }
    }
  },
  { deep: true }
)

watch(
  formData,
  (newValue) => {
    emit('update:modelValue', { ...newValue })
  },
  { deep: true }
)

const validate = async (): Promise<boolean> => {
  if (!formRef.value) return false
  try {
    await formRef.value.validate()
    return true
  } catch {
    return false
  }
}

const resetForm = () => {
  if (formRef.value) {
    formRef.value.resetFields()
  }
  initFormData()
}

const getFormData = (): Record<string, any> => {
  const data: Record<string, any> = {}
  const specialFields = new Set(
    formConfig.value?.fields
      .filter(f => f.type === 'history_select' || f.type === 'url_fetch')
      .map(f => f.name) || []
  )
  
  for (const [key, value] of Object.entries(formData.value)) {
    if (specialFields.has(key)) continue
    if (value !== '' && value !== null && value !== undefined) {
      data[key] = value
    }
  }
  return data
}

defineExpose({
  validate,
  resetForm,
  getFormData,
})

onMounted(() => {
  initFormData()
})
</script>

<style scoped lang="scss">
.dynamic-tool-form {
  :deep(.el-form-item) {
    margin-bottom: 18px;

    .el-form-item__label {
      font-weight: 500;
      color: #303133;
    }
  }

  :deep(.el-textarea__inner) {
    font-family: inherit;
  }

  :deep(.el-input__count) {
    background: transparent;
  }
}

.special-field-wrapper {
  width: 100%;
}

.history-option,
.url-option {
  display: flex;
  flex-direction: column;
  line-height: 1.4;
  padding: 4px 0;

  .option-title {
    font-size: 14px;
    color: #303133;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .option-meta {
    font-size: 12px;
    color: #909399;
    margin-top: 2px;
  }
}

.content-preview {
  margin-top: 8px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 4px;
  border: 1px solid #e4e7ed;

  .preview-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
    font-size: 12px;
    color: #606266;
  }

  .preview-content {
    font-size: 13px;
    color: #303133;
    line-height: 1.6;
    word-break: break-all;
    max-height: 120px;
    overflow: hidden;
  }
}

.url-fetch-input {
  width: 100%;
  
  :deep(.el-input-group__append) {
    padding: 0 15px;
  }
}

.fetch-error {
  margin-top: 8px;
  
  :deep(.el-alert) {
    padding: 8px 12px;
  }
}
</style>
