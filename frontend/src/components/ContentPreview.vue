<template>
  <div class="content-preview">
    <!-- 预览模式切换 -->
    <div class="preview-toolbar">
      <div class="preview-mode-switch">
        <el-radio-group v-model="previewMode" size="small">
          <el-radio-button value="page">
            <el-icon><Monitor /></el-icon>
            <span>页面预览</span>
          </el-radio-button>
          <el-radio-button value="phone">
            <el-icon><Iphone /></el-icon>
            <span>手机预览</span>
          </el-radio-button>
        </el-radio-group>
      </div>
      <div class="preview-actions">
        <el-button 
          v-if="showCopyButton" 
          size="small" 
          @click="copyHtml"
        >
          <el-icon><DocumentCopy /></el-icon>
          复制 HTML
        </el-button>
      </div>
    </div>

    <!-- 页面预览模式 -->
    <div v-if="previewMode === 'page'" class="page-preview">
      <div class="preview-container">
        <div 
          ref="previewContentRef"
          class="preview-content"
          v-html="renderedHtml"
        />
      </div>
    </div>

    <!-- 手机预览模式 -->
    <div v-else class="phone-preview">
      <div class="phone-frame">
        <!-- iPhone 状态栏 -->
        <div class="phone-status-bar">
          <span class="time">{{ currentTime }}</span>
          <div class="status-icons">
            <el-icon><Cellphone /></el-icon>
            <el-icon><Connection /></el-icon>
            <el-icon><Battery /></el-icon>
          </div>
        </div>
        <!-- 微信顶部导航栏 -->
        <div class="wechat-header">
          <el-icon class="back-icon"><ArrowLeft /></el-icon>
          <span class="wechat-title">{{ articleTitle || '文章预览' }}</span>
          <el-icon class="more-icon"><More /></el-icon>
        </div>
        <!-- 文章内容区域 -->
        <div class="phone-content">
          <div 
            ref="phoneContentRef"
            class="wechat-article"
            v-html="renderedHtml"
          />
        </div>
        <!-- iPhone 底部 Home 指示条 -->
        <div class="phone-home-indicator"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { 
  Monitor, 
  Iphone, 
  DocumentCopy, 
  ArrowLeft, 
  More,
  Cellphone,
  Connection,
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { renderWithTemplate, renderForWechat, markdownToHtml } from '@/services/markdownRenderer'
import type { ArticleTemplate } from '@/types/template'

// 自定义 Battery 图标（Element Plus 没有电池图标）
const Battery = {
  template: `<svg viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg">
    <path fill="currentColor" d="M896 320h-64V192c0-35.3-28.7-64-64-64H256c-35.3 0-64 28.7-64 64v640c0 35.3 28.7 64 64 64h512c35.3 0 64-28.7 64-64V704h64c35.3 0 64-28.7 64-64V384c0-35.3-28.7-64-64-64zM768 832H256V192h512v640zm128-192h-64V384h64v256z"/>
  </svg>`
}

const props = withDefaults(defineProps<{
  content: string
  template?: ArticleTemplate | null
  articleTitle?: string
  showCopyButton?: boolean
  isMarkdown?: boolean
}>(), {
  template: null,
  articleTitle: '',
  showCopyButton: true,
  isMarkdown: true
})

const emit = defineEmits<{
  (e: 'copy', html: string): void
}>()

const previewMode = ref<'page' | 'phone'>('page')
const previewContentRef = ref<HTMLElement>()
const phoneContentRef = ref<HTMLElement>()
const currentTime = ref('')

// 渲染后的 HTML
const renderedHtml = computed(() => {
  if (!props.content) return '<p class="empty-hint">暂无内容</p>'
  
  if (props.isMarkdown) {
    // Markdown 内容，应用模板样式
    return renderWithTemplate(props.content, props.template)
  } else {
    // 已经是 HTML 内容
    return props.content
  }
})

// 用于复制的微信格式 HTML
const wechatHtml = computed(() => {
  if (!props.content || !props.isMarkdown) return props.content
  return renderForWechat(props.content, props.template)
})

// 更新时间
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

// 复制 HTML
const copyHtml = async () => {
  try {
    await navigator.clipboard.writeText(wechatHtml.value)
    ElMessage.success('HTML 已复制到剪贴板')
    emit('copy', wechatHtml.value)
  } catch (error) {
    // 降级方案
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
    } catch (e) {
      ElMessage.error('复制失败，请手动复制')
    }
    document.body.removeChild(textarea)
  }
}

// 暴露方法
defineExpose({
  copyHtml,
  getRenderedHtml: () => renderedHtml.value,
  getWechatHtml: () => wechatHtml.value
})
</script>

<style scoped lang="scss">
.content-preview {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #f5f7fa;
  border-radius: 8px;
  overflow: hidden;

  .preview-toolbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 16px;
    background: #fff;
    border-bottom: 1px solid #e4e7ed;

    .preview-mode-switch {
      :deep(.el-radio-button__inner) {
        display: flex;
        align-items: center;
        gap: 4px;
        padding: 6px 12px;
      }
    }
  }

  // 页面预览模式
  .page-preview {
    flex: 1;
    overflow: auto;
    padding: 20px;

    .preview-container {
      max-width: 800px;
      margin: 0 auto;
      background: #fff;
      border-radius: 8px;
      box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
      
      .preview-content {
        padding: 32px;
        min-height: 400px;
        
        :deep(.empty-hint) {
          color: #909399;
          text-align: center;
          padding: 40px 0;
        }

        // 默认预览样式（无模板时）
        :deep(h1) {
          font-size: 24px;
          font-weight: 600;
          margin-bottom: 16px;
          color: #303133;
        }

        :deep(h2) {
          font-size: 20px;
          font-weight: 600;
          margin-top: 24px;
          margin-bottom: 12px;
          color: #303133;
        }

        :deep(h3) {
          font-size: 18px;
          font-weight: 600;
          margin-top: 20px;
          margin-bottom: 10px;
          color: #303133;
        }

        :deep(p) {
          font-size: 15px;
          line-height: 1.8;
          margin-bottom: 12px;
          color: #606266;
        }

        :deep(blockquote) {
          margin: 16px 0;
          padding: 12px 16px;
          background: #f5f7fa;
          border-left: 4px solid #409eff;
          color: #606266;
        }

        :deep(ul), :deep(ol) {
          margin: 12px 0;
          padding-left: 24px;
        }

        :deep(li) {
          font-size: 15px;
          line-height: 1.8;
          color: #606266;
          margin-bottom: 6px;
        }

        :deep(code) {
          font-family: 'Consolas', 'Monaco', monospace;
          font-size: 14px;
          background: #f5f7fa;
          padding: 2px 6px;
          border-radius: 4px;
          color: #e6a23c;
        }

        :deep(pre) {
          background: #2d3748;
          padding: 16px;
          border-radius: 8px;
          overflow-x: auto;
          margin: 16px 0;

          code {
            background: transparent;
            color: #e2e8f0;
            padding: 0;
          }
        }

        :deep(img) {
          max-width: 100%;
          height: auto;
          border-radius: 8px;
          margin: 16px 0;
        }

        :deep(a) {
          color: #409eff;
          text-decoration: none;

          &:hover {
            text-decoration: underline;
          }
        }

        :deep(hr) {
          border: none;
          border-top: 1px solid #e4e7ed;
          margin: 24px 0;
        }
      }
    }
  }

  // 手机预览模式
  .phone-preview {
    flex: 1;
    display: flex;
    justify-content: center;
    align-items: flex-start;
    padding: 20px;
    overflow: auto;

    .phone-frame {
      width: 375px;
      height: 812px;
      background: #fff;
      border-radius: 44px;
      box-shadow: 
        0 0 0 12px #1a1a1a,
        0 0 0 14px #333,
        0 20px 60px rgba(0, 0, 0, 0.3);
      overflow: hidden;
      display: flex;
      flex-direction: column;
      position: relative;

      // 刘海
      &::before {
        content: '';
        position: absolute;
        top: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 150px;
        height: 30px;
        background: #1a1a1a;
        border-radius: 0 0 20px 20px;
        z-index: 10;
      }

      // 状态栏
      .phone-status-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 14px 24px 8px;
        font-size: 14px;
        font-weight: 500;
        background: #ededed;

        .time {
          font-weight: 600;
        }

        .status-icons {
          display: flex;
          gap: 4px;
          font-size: 16px;
        }
      }

      // 微信顶部导航
      .wechat-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 10px 16px;
        background: #ededed;
        border-bottom: 1px solid #d9d9d9;

        .back-icon {
          font-size: 20px;
          color: #000;
        }

        .wechat-title {
          font-size: 17px;
          font-weight: 500;
          color: #000;
          flex: 1;
          text-align: center;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
          padding: 0 40px;
        }

        .more-icon {
          font-size: 20px;
          color: #000;
        }
      }

      // 文章内容区域
      .phone-content {
        flex: 1;
        overflow-y: auto;
        background: #fff;

        .wechat-article {
          padding: 20px 16px;

          :deep(.empty-hint) {
            color: #909399;
            text-align: center;
            padding: 40px 0;
            font-size: 14px;
          }

          // 微信文章默认样式
          :deep(h1) {
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 12px;
            color: #333;
          }

          :deep(h2) {
            font-size: 18px;
            font-weight: 600;
            margin-top: 20px;
            margin-bottom: 10px;
            color: #333;
          }

          :deep(h3) {
            font-size: 16px;
            font-weight: 600;
            margin-top: 16px;
            margin-bottom: 8px;
            color: #333;
          }

          :deep(p) {
            font-size: 15px;
            line-height: 1.8;
            margin-bottom: 10px;
            color: #333;
            text-align: justify;
          }

          :deep(blockquote) {
            margin: 12px 0;
            padding: 10px 12px;
            background: #f7f7f7;
            border-left: 3px solid #07c160;
            color: #666;
            font-size: 14px;
          }

          :deep(ul), :deep(ol) {
            margin: 10px 0;
            padding-left: 20px;
          }

          :deep(li) {
            font-size: 15px;
            line-height: 1.8;
            color: #333;
            margin-bottom: 4px;
          }

          :deep(code) {
            font-family: 'Menlo', monospace;
            font-size: 13px;
            background: #f5f5f5;
            padding: 2px 4px;
            border-radius: 3px;
            color: #e6a23c;
          }

          :deep(pre) {
            background: #2d3748;
            padding: 12px;
            border-radius: 6px;
            overflow-x: auto;
            margin: 12px 0;
            font-size: 13px;

            code {
              background: transparent;
              color: #e2e8f0;
              padding: 0;
            }
          }

          :deep(img) {
            max-width: 100%;
            height: auto;
            border-radius: 4px;
            margin: 12px 0;
          }

          :deep(a) {
            color: #576b95;
            text-decoration: none;
          }

          :deep(hr) {
            border: none;
            border-top: 1px solid #e5e5e5;
            margin: 20px 0;
          }
        }
      }

      // 底部 Home 指示条
      .phone-home-indicator {
        height: 34px;
        background: #fff;
        display: flex;
        align-items: center;
        justify-content: center;

        &::after {
          content: '';
          width: 134px;
          height: 5px;
          background: #1a1a1a;
          border-radius: 3px;
        }
      }
    }
  }
}
</style>
