<template>
  <div class="content-preview">
    <div class="preview-toolbar">
      <el-radio-group v-model="previewMode" size="small" class="preview-mode-switch">
        <el-radio-button label="page">
          <span class="mode-label">
            <el-icon><Monitor /></el-icon>
            页面预览
          </span>
        </el-radio-button>
        <el-radio-button label="phone">
          <span class="mode-label">
            <el-icon><Iphone /></el-icon>
            手机预览
          </span>
        </el-radio-button>
      </el-radio-group>

      <el-button v-if="showCopyButton" size="small" @click="copyHtml">
        <el-icon><DocumentCopy /></el-icon>
        复制 HTML
      </el-button>
    </div>

    <div v-if="previewMode === 'page'" class="page-preview">
      <div class="preview-container">
        <div class="preview-content" v-html="renderedHtml" />
      </div>
    </div>

    <div v-else class="phone-preview">
      <div class="phone-frame">
        <div class="phone-status-bar">
          <span class="time">{{ currentTime }}</span>
          <div class="status-icons">
            <el-icon><Cellphone /></el-icon>
            <el-icon><Connection /></el-icon>
            <el-icon><Battery /></el-icon>
          </div>
        </div>
        <div class="wechat-header">
          <el-icon class="back-icon"><ArrowLeft /></el-icon>
          <span class="wechat-title">{{ articleTitle || '文章预览' }}</span>
          <el-icon class="more-icon"><MoreFilled /></el-icon>
        </div>
        <div class="phone-content">
          <div class="wechat-article" v-html="renderedHtml" />
        </div>
        <div class="phone-home-indicator"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import {
  Monitor,
  Iphone,
  DocumentCopy,
  ArrowLeft,
  MoreFilled,
  Cellphone,
  Connection,
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { renderWithTemplate, renderForWechat } from '@/services/markdownRenderer'
import type { ArticleTemplate } from '@/types/template'

const Battery = {
  template: `<svg viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg"><path fill="currentColor" d="M896 320h-64V192c0-35.3-28.7-64-64-64H256c-35.3 0-64 28.7-64 64v640c0 35.3 28.7 64 64 64h512c35.3 0 64-28.7 64-64V704h64c35.3 0 64-28.7 64-64V384c0-35.3-28.7-64-64-64zM768 832H256V192h512v640zm128-192h-64V384h64v256z"/></svg>`,
}

const props = withDefaults(
  defineProps<{
    content: string
    template?: ArticleTemplate | null
    articleTitle?: string
    showCopyButton?: boolean
    isMarkdown?: boolean
  }>(),
  {
    template: null,
    articleTitle: '',
    showCopyButton: true,
    isMarkdown: true,
  }
)

const emit = defineEmits<{
  (e: 'copy', html: string): void
}>()

const previewMode = ref<'page' | 'phone'>('page')
const currentTime = ref('')

const renderedHtml = computed(() => {
  if (!props.content) {
    return '<p class="empty-hint">暂无内容可预览</p>'
  }

  if (props.isMarkdown) {
    return renderWithTemplate(props.content, props.template)
  }

  return props.content
})

const wechatHtml = computed(() => {
  if (!props.content || !props.isMarkdown) return props.content
  return renderForWechat(props.content, props.template)
})

const updateTime = () => {
  const now = new Date()
  const hours = now.getHours().toString().padStart(2, '0')
  const minutes = now.getMinutes().toString().padStart(2, '0')
  currentTime.value = `${hours}:${minutes}`
}

let timeInterval: ReturnType<typeof setInterval>

onMounted(() => {
  updateTime()
  timeInterval = setInterval(updateTime, 60000)
})

onUnmounted(() => {
  if (timeInterval) {
    clearInterval(timeInterval)
  }
})

const copyHtml = async () => {
  try {
    await navigator.clipboard.writeText(wechatHtml.value)
    ElMessage.success('HTML 已复制到剪贴板')
    emit('copy', wechatHtml.value)
  } catch (error) {
    const textarea = document.createElement('textarea')
    textarea.value = wechatHtml.value
    textarea.style.position = 'fixed'
    textarea.style.opacity = '0'
    document.body.appendChild(textarea)
    textarea.select()
    try {
      document.execCommand('copy')
      ElMessage.success('HTML 已复制到剪贴板')
      emit('copy', wechatHtml.value)
    } catch (_e) {
      ElMessage.error('复制失败，请手动复制')
    }
    document.body.removeChild(textarea)
  }
}

defineExpose({
  copyHtml,
  getRenderedHtml: () => renderedHtml.value,
  getWechatHtml: () => wechatHtml.value,
})
</script>

<style scoped lang="scss">
.content-preview {
  display: flex;
  flex-direction: column;
  min-height: 100%;
  background: linear-gradient(180deg, rgba(248, 250, 252, 0.96), rgba(239, 246, 255, 0.85));
  border: 1px solid rgba(148, 163, 184, 0.18);
  border-radius: 24px;
  overflow: hidden;
}

.preview-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 16px 18px;
  background: rgba(255, 255, 255, 0.82);
  border-bottom: 1px solid rgba(148, 163, 184, 0.16);
}

.preview-mode-switch :deep(.el-radio-button__inner) {
  padding: 8px 14px;
}

.mode-label {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.page-preview {
  flex: 1;
  padding: 22px;
  overflow: auto;
}

.preview-container {
  max-width: 840px;
  margin: 0 auto;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 22px 50px rgba(15, 23, 42, 0.12);
}

.preview-content {
  min-height: 420px;
  padding: 32px;
}

.preview-content :deep(.empty-hint) {
  margin: 0;
  padding: 48px 0;
  text-align: center;
  color: #6b7280;
}

.phone-preview {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}

.phone-frame {
  width: min(100%, 390px);
  min-height: 720px;
  display: flex;
  flex-direction: column;
  border-radius: 36px;
  background: #101828;
  box-shadow: 0 26px 70px rgba(15, 23, 42, 0.25);
  overflow: hidden;
}

.phone-status-bar,
.wechat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 18px;
  color: #f8fafc;
}

.phone-status-bar {
  font-size: 12px;
}

.status-icons,
.mode-label {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.wechat-header {
  padding-top: 10px;
  padding-bottom: 14px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.wechat-title {
  flex: 1;
  text-align: center;
  font-size: 14px;
  font-weight: 600;
}

.back-icon,
.more-icon {
  width: 20px;
}

.phone-content {
  flex: 1;
  padding: 14px;
  background: #e5e7eb;
  overflow: auto;
}

.wechat-article {
  min-height: 100%;
  padding: 20px 16px 36px;
  border-radius: 24px;
  background: #fff;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.8);
}

.phone-home-indicator {
  width: 120px;
  height: 5px;
  margin: 12px auto 16px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.72);
}

@media (max-width: 768px) {
  .preview-toolbar {
    flex-direction: column;
    align-items: stretch;
  }

  .page-preview,
  .phone-preview {
    padding: 14px;
  }

  .preview-content {
    padding: 20px;
  }

  .phone-frame {
    min-height: 620px;
    border-radius: 28px;
  }
}
</style>
