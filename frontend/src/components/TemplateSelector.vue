<template>
  <div class="template-selector">
    <div class="template-header">
      <div>
        <div class="title">排版模板</div>
        <div class="subtitle">选择一个模板，为文章预览和导出 HTML 应用统一样式。</div>
      </div>
      <el-button link type="primary" size="small" @click="$emit('manage')">管理模板</el-button>
    </div>

    <!-- 平台选择 -->
    <div class="platform-selector">
      <div
        v-for="p in platforms"
        :key="p.id"
        class="platform-item"
        :class="{ active: selectedPlatform === p.id }"
        @click="selectPlatform(p.id)"
      >
        <span class="platform-icon">{{ getPlatformIcon(p.id) }}</span>
        <span class="platform-name">{{ p.name }}</span>
      </div>
    </div>

    <!-- 场景筛选 -->
    <div v-if="currentCategories.length > 0" class="category-filter">
      <el-tag
        v-for="cat in currentCategories"
        :key="cat.id"
        :type="selectedCategory === cat.id ? '' : 'info'"
        :effect="selectedCategory === cat.id ? 'dark' : 'plain'"
        class="category-tag"
        @click="selectCategory(cat.id)"
      >
        {{ cat.name }}
      </el-tag>
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
import { ref, onMounted, watch, computed } from 'vue'
import { Check } from '@element-plus/icons-vue'
import { getTemplates, getPlatforms } from '@/api/templates'
import type { ContentTemplate, CSSProperties, PlatformType, PlatformInfo } from '@/types/template'

const props = defineProps<{
  modelValue?: number
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: number): void
  (e: 'change', template: ContentTemplate): void
  (e: 'manage'): void
}>()

const platforms = ref<PlatformInfo[]>([])
const selectedPlatform = ref<PlatformType>('wechat')
const selectedCategory = ref<string>('')
const templates = ref<ContentTemplate[]>([])
const loading = ref(false)

const currentCategories = computed(() => {
  const platform = platforms.value.find(p => p.id === selectedPlatform.value)
  return platform?.categories || []
})

const selectPlatform = (platform: PlatformType) => {
  selectedPlatform.value = platform
  selectedCategory.value = ''
  loadTemplates()
}

const selectCategory = (category: string) => {
  selectedCategory.value = selectedCategory.value === category ? '' : category
  loadTemplates()
}

const selectTemplate = (template: ContentTemplate) => {
  emit('update:modelValue', template.id)
  emit('change', template)
}

const getPlatformIcon = (platform: PlatformType): string => {
  const icons: Record<PlatformType, string> = {
    wechat: '📱',
    xiaohongshu: '📕',
    toutiao: '📰',
    ppt: '📊',
    douyin: '🎬'
  }
  return icons[platform] || '📄'
}

const loadPlatforms = async () => {
  try {
    const res = await getPlatforms()
    platforms.value = res.platforms || []
    if (platforms.value.length > 0 && !selectedPlatform.value) {
      selectedPlatform.value = platforms.value[0].id
    }
  } catch (error) {
    console.error('加载平台列表失败:', error)
  }
}

const loadTemplates = async () => {
  loading.value = true
  try {
    const params: any = { limit: 50 }
    if (selectedPlatform.value) {
      params.platform = selectedPlatform.value
    }
    if (selectedCategory.value) {
      params.category = selectedCategory.value
    }
    const res = await getTemplates(params)
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

const getPreviewStyle = (template: ContentTemplate): Record<string, string> => {
  const container = template.styles?.container
  if (!container) return {}

  return {
    backgroundColor: container.backgroundColor || '#ffffff',
    fontFamily: container.fontFamily || 'inherit',
  }
}

const getElementStyle = (template: ContentTemplate, element: string): Record<string, string> => {
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

onMounted(async () => {
  await loadPlatforms()
  await loadTemplates()
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

.platform-selector {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.platform-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 12px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: #f1f5f9;
    border-color: #cbd5e1;
  }

  &.active {
    background: linear-gradient(135deg, #3b82f6, #2563eb);
    border-color: transparent;
    color: #fff;
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
  }
}

.platform-icon {
  font-size: 18px;
}

.platform-name {
  font-size: 14px;
  font-weight: 500;
}

.category-filter {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.category-tag {
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    transform: translateY(-1px);
  }
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

  .platform-selector {
    flex-wrap: nowrap;
    overflow-x: auto;
    padding-bottom: 8px;
  }
}
</style>
