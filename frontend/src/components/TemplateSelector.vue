<template>
  <div class="template-selector">
    <div class="template-header">
      <div>
        <div class="title">排版模板</div>
        <div class="subtitle">选择一个模板，为文章预览和导出 HTML 应用统一样式。</div>
      </div>
      <el-button link type="primary" size="small" @click="$emit('manage')">管理模板</el-button>
    </div>

    <div v-if="loading" class="state-block">
      <el-skeleton :rows="3" animated />
    </div>

    <el-empty v-else-if="templates.length === 0" description="暂无可用模板" :image-size="72" />

    <div v-else class="template-grid">
      <button
        v-for="template in templates"
        :key="template.id"
        type="button"
        class="template-card"
        :class="{ active: modelValue === template.id }"
        @click="selectTemplate(template)"
      >
        <div class="template-preview">
          <div class="preview-content" :style="getPreviewStyle(template)">
            <div class="preview-h1" :style="getElementStyle(template, 'h1')">主标题示例</div>
            <div class="preview-p" :style="getElementStyle(template, 'p')">正文排版预览</div>
            <div class="preview-quote" :style="getElementStyle(template, 'blockquote')">引用内容</div>
          </div>
        </div>
        <div class="template-info">
          <div class="name-row">
            <span class="name">{{ template.name }}</span>
            <el-tag v-if="template.is_system" size="small" effect="plain">系统</el-tag>
            <el-tag v-else size="small" type="success" effect="plain">自定义</el-tag>
          </div>
          <p class="desc">{{ template.description || '用于控制标题、正文、引用等排版样式。' }}</p>
        </div>
        <div v-if="modelValue === template.id" class="selected-badge">
          <el-icon><Check /></el-icon>
        </div>
      </button>
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

const selectTemplate = (template: ArticleTemplate) => {
  emit('update:modelValue', template.id)
  emit('change', template)
}

const loadTemplates = async () => {
  loading.value = true
  try {
    const res = await getTemplates({ limit: 50 })
    templates.value = res.items || []

    if (!props.modelValue && templates.value.length > 0) {
      selectTemplate(templates.value[0])
    }
  } catch (error) {
    console.error('加载模板失败:', error)
  } finally {
    loading.value = false
  }
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

watch(
  () => props.modelValue,
  (newVal) => {
    if (!newVal) return
    const template = templates.value.find((item) => item.id === newVal)
    if (template) {
      emit('change', template)
    }
  }
)

onMounted(() => {
  loadTemplates()
})

defineExpose({
  refresh: loadTemplates,
})
</script>

<style scoped lang="scss">
.template-selector {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.template-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.title {
  font-size: 16px;
  font-weight: 700;
  color: #12304a;
}

.subtitle {
  margin-top: 6px;
  font-size: 13px;
  line-height: 1.6;
  color: #5f7690;
}

.state-block {
  padding: 12px 0;
}

.template-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 14px;
}

.template-card {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 14px;
  text-align: left;
  border: 1px solid rgba(148, 163, 184, 0.22);
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.88);
  box-shadow: 0 18px 44px rgba(15, 23, 42, 0.08);
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}

.template-card:hover {
  transform: translateY(-2px);
  border-color: rgba(59, 130, 246, 0.36);
  box-shadow: 0 22px 48px rgba(37, 99, 235, 0.14);
}

.template-card.active {
  border-color: rgba(37, 99, 235, 0.5);
  box-shadow: 0 26px 56px rgba(37, 99, 235, 0.18);
}

.template-preview {
  padding: 10px;
  border-radius: 16px;
  background: linear-gradient(180deg, rgba(239, 246, 255, 0.96), rgba(248, 250, 252, 0.92));
}

.preview-content {
  min-height: 112px;
  padding: 12px;
  border-radius: 12px;
  overflow: hidden;
}

.preview-h1,
.preview-p,
.preview-quote {
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.preview-h1 {
  font-size: 12px;
  font-weight: 700;
  margin-bottom: 8px;
}

.preview-p {
  font-size: 10px;
  margin-bottom: 8px;
}

.preview-quote {
  display: inline-flex;
  max-width: 100%;
  padding: 4px 8px;
  font-size: 9px;
  border-radius: 999px;
  background: rgba(15, 23, 42, 0.06);
}

.template-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.name-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.name {
  flex: 1;
  font-size: 14px;
  font-weight: 700;
  color: #12304a;
}

.desc {
  margin: 0;
  font-size: 12px;
  line-height: 1.6;
  color: #60758e;
}

.selected-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 999px;
  color: #fff;
  background: linear-gradient(135deg, #2563eb, #38bdf8);
  box-shadow: 0 10px 24px rgba(37, 99, 235, 0.28);
}

@media (max-width: 768px) {
  .template-header {
    flex-direction: column;
  }

  .template-grid {
    grid-template-columns: 1fr;
  }
}
</style>
