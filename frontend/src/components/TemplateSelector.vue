<template>
  <div class="template-selector">
    <div class="template-header">
      <span class="title">选择模板</span>
      <el-button link type="primary" size="small" @click="$emit('manage')">
        管理模板
      </el-button>
    </div>
    
    <div v-if="loading" class="loading-state">
      <el-skeleton :rows="2" animated />
    </div>
    
    <div v-else-if="templates.length === 0" class="empty-state">
      <el-empty description="暂无可用模板" :image-size="60" />
    </div>
    
    <div v-else class="template-grid">
      <div
        v-for="template in templates"
        :key="template.id"
        :class="['template-card', { active: modelValue === template.id }]"
        @click="selectTemplate(template)"
      >
        <div class="template-preview">
          <div 
            class="preview-content"
            :style="getPreviewStyle(template)"
          >
            <div class="preview-h1" :style="getElementStyle(template, 'h1')">标题</div>
            <div class="preview-p" :style="getElementStyle(template, 'p')">正文内容示例</div>
            <div class="preview-quote" :style="getElementStyle(template, 'blockquote')">引用</div>
          </div>
        </div>
        <div class="template-info">
          <span class="name">{{ template.name }}</span>
          <div class="tags">
            <el-tag v-if="template.is_system" size="small" type="info">系统</el-tag>
            <el-tag v-else size="small" type="success">自定义</el-tag>
          </div>
        </div>
        <div v-if="modelValue === template.id" class="selected-badge">
          <el-icon><Check /></el-icon>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { Check } from '@element-plus/icons-vue'
import { getTemplates } from '@/api/templates'
import type { ArticleTemplate, CSSProperties } from '@/types/template'

const props = defineProps<{
  modelValue?: number
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: number): void
  (e: 'change', template: ArticleTemplate): void
  (e: 'manage'): void
}>()

const templates = ref<ArticleTemplate[]>([])
const loading = ref(false)

const loadTemplates = async () => {
  loading.value = true
  try {
    const res = await getTemplates({ limit: 50 })
    templates.value = res.items
    
    // 如果没有选中模板且有模板列表，默认选中第一个
    if (!props.modelValue && templates.value.length > 0) {
      selectTemplate(templates.value[0])
    }
  } catch (error) {
    console.error('加载模板失败:', error)
  } finally {
    loading.value = false
  }
}

const selectTemplate = (template: ArticleTemplate) => {
  emit('update:modelValue', template.id)
  emit('change', template)
}

const getPreviewStyle = (template: ArticleTemplate): Record<string, string> => {
  const container = template.styles?.container
  if (!container) return {}
  
  return {
    backgroundColor: container.backgroundColor || '#ffffff',
    fontFamily: container.fontFamily || 'inherit',
  }
}

const getElementStyle = (template: ArticleTemplate, element: string): Record<string, string> => {
  const styles = template.styles?.[element] as CSSProperties
  if (!styles) return {}
  
  const result: Record<string, string> = {}
  
  if (styles.color) result.color = styles.color
  if (styles.fontSize) result.fontSize = styles.fontSize
  if (styles.fontWeight) result.fontWeight = styles.fontWeight
  if (styles.borderLeft) result.borderLeft = styles.borderLeft
  if (styles.borderBottom) result.borderBottom = styles.borderBottom
  if (styles.backgroundColor) result.backgroundColor = styles.backgroundColor
  if (styles.paddingLeft) result.paddingLeft = styles.paddingLeft
  
  return result
}

// 当外部传入的 modelValue 变化时，触发 change 事件
watch(() => props.modelValue, (newVal) => {
  if (newVal) {
    const template = templates.value.find(t => t.id === newVal)
    if (template) {
      emit('change', template)
    }
  }
})

onMounted(() => {
  loadTemplates()
})

defineExpose({
  refresh: loadTemplates
})
</script>

<style scoped lang="scss">
.template-selector {
  .template-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    
    .title {
      font-size: 14px;
      font-weight: 500;
      color: #303133;
    }
  }
  
  .loading-state,
  .empty-state {
    padding: 20px 0;
  }
  
  .template-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: 12px;
  }
  
  .template-card {
    position: relative;
    border: 2px solid #e4e7ed;
    border-radius: 8px;
    overflow: hidden;
    cursor: pointer;
    transition: all 0.2s ease;
    
    &:hover {
      border-color: #409eff;
      box-shadow: 0 2px 12px rgba(64, 158, 255, 0.15);
    }
    
    &.active {
      border-color: #409eff;
      
      .selected-badge {
        display: flex;
      }
    }
    
    .template-preview {
      height: 100px;
      padding: 8px;
      background: #f5f7fa;
      
      .preview-content {
        height: 100%;
        padding: 6px;
        border-radius: 4px;
        overflow: hidden;
        
        .preview-h1 {
          font-size: 10px;
          font-weight: 600;
          margin-bottom: 4px;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }
        
        .preview-p {
          font-size: 8px;
          margin-bottom: 4px;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }
        
        .preview-quote {
          font-size: 7px;
          padding: 2px 4px;
          border-radius: 2px;
        }
      }
    }
    
    .template-info {
      padding: 8px;
      background: #fff;
      
      .name {
        display: block;
        font-size: 12px;
        font-weight: 500;
        color: #303133;
        margin-bottom: 4px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }
      
      .tags {
        display: flex;
        gap: 4px;
        
        .el-tag {
          font-size: 10px;
          height: 18px;
          line-height: 16px;
          padding: 0 4px;
        }
      }
    }
    
    .selected-badge {
      display: none;
      position: absolute;
      top: 6px;
      right: 6px;
      width: 20px;
      height: 20px;
      background: #409eff;
      border-radius: 50%;
      align-items: center;
      justify-content: center;
      color: #fff;
      font-size: 12px;
    }
  }
}
</style>
