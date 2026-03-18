<template>
  <el-dialog
    v-model="dialogVisible"
    title="AI 选题建议"
    width="640px"
    :close-on-click-modal="false"
  >
    <div class="suggest-dialog">
      <div class="hot-title">
        <el-icon><TrendCharts /></el-icon>
        <span>{{ hotTitle }}</span>
      </div>

      <div v-if="loading" class="loading-state">
        <el-icon class="loading-icon"><Loading /></el-icon>
        <p>AI 正在分析热点，生成选题建议...</p>
      </div>

      <template v-else-if="suggestions">
        <div class="background-section">
          <h4>热点背景</h4>
          <p>{{ suggestions.background }}</p>
        </div>

        <div class="keywords-section">
          <h4>相关关键词</h4>
          <div class="keywords">
            <el-tag v-for="keyword in suggestions.keywords" :key="keyword" size="small">
              {{ keyword }}
            </el-tag>
          </div>
        </div>

        <div class="angles-section">
          <h4>创作角度建议</h4>
          <div class="angles-list">
            <div
              v-for="(angle, index) in suggestions.angles"
              :key="index"
              class="angle-card"
              :class="{ selected: selectedAngleIndex === index }"
              @click="selectedAngleIndex = index"
            >
              <div class="angle-header">
                <span class="angle-index">{{ index + 1 }}</span>
                <span class="angle-name">{{ angle.angle }}</span>
              </div>
              <div class="angle-title">
                <el-icon><Document /></el-icon>
                {{ angle.title_suggestion }}
              </div>
              <div class="angle-direction">
                {{ angle.content_direction }}
              </div>
              <div class="angle-meta">
                <div class="tools">
                  <span class="label">推荐工具：</span>
                  <el-tag
                    v-for="tool in angle.recommended_tools"
                    :key="tool"
                    size="small"
                    type="success"
                  >
                    {{ getToolName(tool) }}
                  </el-tag>
                </div>
                <div class="audience">
                  <span class="label">目标受众：</span>
                  {{ angle.target_audience }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>

      <div v-else class="error-state">
        <el-icon><WarningFilled /></el-icon>
        <p>获取选题建议失败，请重试</p>
        <el-button type="primary" @click="loadSuggestions">重新获取</el-button>
      </div>
    </div>

    <template #footer>
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button
        type="primary"
        :disabled="selectedAngleIndex === null || !suggestions"
        @click="confirmSelection"
      >
        使用该角度写作
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { TrendCharts, Loading, Document, WarningFilled } from '@element-plus/icons-vue'
import { getTopicSuggestions } from '@/api/hotspot'
import type { TopicSuggestResponse } from '@/api/hotspot'

const props = defineProps<{
  visible: boolean
  hotTitle: string
}>()

const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
  (e: 'select', data: { toolType: string; title: string; direction: string }): void
}>()

const dialogVisible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value),
})

const loading = ref(false)
const suggestions = ref<TopicSuggestResponse | null>(null)
const selectedAngleIndex = ref<number | null>(null)

// 工具名称映射
const toolNameMap: Record<string, string> = {
  wechat_article: '公众号文章',
  xiaohongshu_note: '小红书笔记',
  video_script: '短视频脚本',
  news_article: '新闻稿',
  marketing_copy: '营销文案',
  official_document: '公文写作',
  academic_paper: '论文写作',
}

const getToolName = (toolType: string) => {
  return toolNameMap[toolType] || toolType
}

// 加载选题建议
const loadSuggestions = async () => {
  if (!props.hotTitle) return

  loading.value = true
  suggestions.value = null
  selectedAngleIndex.value = null

  try {
    const res = await getTopicSuggestions({
      hot_title: props.hotTitle,
    })
    suggestions.value = res
    // 默认选中第一个角度
    if (res.angles && res.angles.length > 0) {
      selectedAngleIndex.value = 0
    }
  } catch (error) {
    console.error('获取选题建议失败:', error)
  } finally {
    loading.value = false
  }
}

// 确认选择
const confirmSelection = () => {
  if (selectedAngleIndex.value === null || !suggestions.value) return

  const angle = suggestions.value.angles[selectedAngleIndex.value]
  const toolType = angle.recommended_tools[0] || 'wechat_article'

  emit('select', {
    toolType,
    title: angle.title_suggestion,
    direction: angle.content_direction,
  })
  dialogVisible.value = false
}

// 监听弹窗打开
watch(
  () => props.visible,
  (visible) => {
    if (visible && props.hotTitle) {
      loadSuggestions()
    }
  }
)
</script>

<style scoped lang="scss">
.suggest-dialog {
  .hot-title {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 12px 16px;
    background: linear-gradient(135deg, #fef3c7, #fde68a);
    border-radius: 8px;
    margin-bottom: 20px;
    font-size: 15px;
    font-weight: 500;
    color: #92400e;

    .el-icon {
      color: #f59e0b;
    }
  }

  .loading-state {
    text-align: center;
    padding: 40px 0;

    .loading-icon {
      font-size: 32px;
      color: #3b82f6;
      animation: spin 1s linear infinite;
    }

    p {
      margin-top: 12px;
      color: #64748b;
    }
  }

  .error-state {
    text-align: center;
    padding: 40px 0;

    .el-icon {
      font-size: 48px;
      color: #f59e0b;
    }

    p {
      margin: 12px 0 16px;
      color: #64748b;
    }
  }

  .background-section,
  .keywords-section,
  .angles-section {
    margin-bottom: 20px;

    h4 {
      font-size: 14px;
      font-weight: 600;
      color: #334155;
      margin-bottom: 8px;
    }
  }

  .background-section p {
    font-size: 14px;
    line-height: 1.6;
    color: #64748b;
    margin: 0;
  }

  .keywords {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  .angles-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .angle-card {
    padding: 16px;
    border: 2px solid #e2e8f0;
    border-radius: 12px;
    cursor: pointer;
    transition: all 0.2s;

    &:hover {
      border-color: #93c5fd;
      background: #f0f9ff;
    }

    &.selected {
      border-color: #3b82f6;
      background: #eff6ff;
    }

    .angle-header {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 8px;

      .angle-index {
        width: 24px;
        height: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: #3b82f6;
        color: white;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 600;
      }

      .angle-name {
        font-size: 15px;
        font-weight: 600;
        color: #1e293b;
      }
    }

    .angle-title {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 14px;
      color: #3b82f6;
      margin-bottom: 8px;

      .el-icon {
        flex-shrink: 0;
      }
    }

    .angle-direction {
      font-size: 13px;
      line-height: 1.5;
      color: #64748b;
      margin-bottom: 12px;
    }

    .angle-meta {
      display: flex;
      flex-direction: column;
      gap: 6px;
      font-size: 12px;

      .label {
        color: #94a3b8;
      }

      .tools {
        display: flex;
        align-items: center;
        gap: 6px;
        flex-wrap: wrap;
      }

      .audience {
        color: #64748b;
      }
    }
  }
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
