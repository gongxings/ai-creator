<template>
  <div class="title-optimizer">
    <el-card class="optimizer-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span class="title">
            <el-icon><MagicStick /></el-icon>
            标题优化助手
          </span>
          <el-tooltip content="AI 分析您的标题，提供优化建议和多个高分版本">
            <el-icon class="help-icon"><QuestionFilled /></el-icon>
          </el-tooltip>
        </div>
      </template>

      <el-form :model="form" label-position="top">
        <el-form-item label="当前标题">
          <el-input
            v-model="form.originalTitle"
            placeholder="输入您想要优化的标题"
            :maxlength="200"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="目标平台">
          <el-select v-model="form.platform" placeholder="选择目标平台（可选）" clearable>
            <el-option
              v-for="p in platforms"
              :key="p.value"
              :label="p.label"
              :value="p.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            :loading="loading"
            :disabled="!form.originalTitle.trim()"
            @click="handleOptimize"
          >
            <el-icon><MagicStick /></el-icon>
            AI 优化标题
          </el-button>
          <el-button @click="handleAnalyze" :loading="analyzing" :disabled="!form.originalTitle.trim()">
            <el-icon><DataAnalysis /></el-icon>
            分析标题
          </el-button>
        </el-form-item>
      </el-form>

      <!-- 分析结果 -->
      <div v-if="analyzeResult" class="analyze-result">
        <div class="score-section">
          <div class="score-circle" :style="{ '--score-color': getScoreColor(analyzeResult.score) }">
            <span class="score-value">{{ analyzeResult.score }}</span>
            <span class="score-label">爆款指数</span>
          </div>
          <div class="score-info">
            <el-tag :type="getScoreType(analyzeResult.score)" size="large">
              {{ getScoreLabel(analyzeResult.score) }}
            </el-tag>
            <p class="style-info">风格：{{ STYLE_LABELS[analyzeResult.style] || analyzeResult.style }}</p>
          </div>
        </div>

        <el-collapse>
          <el-collapse-item title="优点" name="strengths">
            <ul class="feedback-list strengths">
              <li v-for="(item, idx) in analyzeResult.strengths" :key="idx">
                <el-icon><SuccessFilled /></el-icon>
                {{ item }}
              </li>
            </ul>
          </el-collapse-item>
          <el-collapse-item title="待改进" name="weaknesses">
            <ul class="feedback-list weaknesses">
              <li v-for="(item, idx) in analyzeResult.weaknesses" :key="idx">
                <el-icon><WarningFilled /></el-icon>
                {{ item }}
              </li>
            </ul>
          </el-collapse-item>
          <el-collapse-item title="改进建议" name="suggestions">
            <ul class="feedback-list suggestions">
              <li v-for="(item, idx) in analyzeResult.improvement_suggestions" :key="idx">
                <el-icon><InfoFilled /></el-icon>
                {{ item }}
              </li>
            </ul>
          </el-collapse-item>
        </el-collapse>
      </div>

      <!-- 优化结果 -->
      <div v-if="optimizeResult" class="optimize-result">
        <div class="original-analysis">
          <h4>原标题分析</h4>
          <div class="original-score">
            <span>原始分数：</span>
            <el-tag :type="getScoreType(optimizeResult.original_score)">
              {{ optimizeResult.original_score }} 分
            </el-tag>
          </div>
          <div v-if="optimizeResult.original_issues.length > 0" class="issues">
            <p>问题诊断：</p>
            <ul>
              <li v-for="(issue, idx) in optimizeResult.original_issues" :key="idx">{{ issue }}</li>
            </ul>
          </div>
        </div>

        <el-divider>优化后的标题</el-divider>

        <div class="optimized-titles">
          <div
            v-for="(item, idx) in optimizeResult.optimized_titles"
            :key="idx"
            class="title-item"
            :class="{ selected: selectedTitle === item.title }"
            @click="selectTitle(item)"
          >
            <div class="title-content">
              <span class="title-text">{{ item.title }}</span>
              <div class="title-meta">
                <el-tag size="small" :color="getScoreColor(item.score)" effect="dark">
                  {{ item.score }}分
                </el-tag>
                <el-tag size="small" type="info">{{ STYLE_LABELS[item.style] || item.style }}</el-tag>
              </div>
            </div>
            <div class="title-hooks">
              <el-tag v-for="hook in item.hooks" :key="hook" size="small" type="warning">
                {{ hook }}
              </el-tag>
            </div>
            <p v-if="item.explanation" class="title-explanation">{{ item.explanation }}</p>
          </div>
        </div>

        <div v-if="optimizeResult.improvement_tips.length > 0" class="improvement-tips">
          <h4>写作建议</h4>
          <ul>
            <li v-for="(tip, idx) in optimizeResult.improvement_tips" :key="idx">{{ tip }}</li>
          </ul>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import {
  MagicStick,
  QuestionFilled,
  DataAnalysis,
  SuccessFilled,
  WarningFilled,
  InfoFilled,
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import {
  optimizeTitle,
  analyzeTitle,
  PlatformType,
  TitleStyle,
  STYLE_LABELS,
  getScoreColor,
  getScoreLabel,
  type TitleOptimizeResponse,
  type TitleAnalyzeResponse,
} from '@/api/title'

// Props
const props = defineProps<{
  initialTitle?: string
}>()

// Emits
const emit = defineEmits<{
  (e: 'select', title: string): void
}>()

// 状态
const loading = ref(false)
const analyzing = ref(false)
const optimizeResult = ref<TitleOptimizeResponse | null>(null)
const analyzeResult = ref<TitleAnalyzeResponse | null>(null)
const selectedTitle = ref('')

// 表单数据
const form = reactive({
  originalTitle: props.initialTitle || '',
  platform: undefined as PlatformType | undefined,
})

// 平台选项
const platforms = [
  { value: PlatformType.WECHAT, label: '微信公众号' },
  { value: PlatformType.XIAOHONGSHU, label: '小红书' },
  { value: PlatformType.DOUYIN, label: '抖音' },
  { value: PlatformType.ZHIHU, label: '知乎' },
  { value: PlatformType.WEIBO, label: '微博' },
  { value: PlatformType.TOUTIAO, label: '今日头条' },
  { value: PlatformType.BILIBILI, label: 'B站' },
]

// 获取分数类型
const getScoreType = (score: number) => {
  if (score >= 90) return 'success'
  if (score >= 70) return 'primary'
  if (score >= 50) return 'warning'
  return 'danger'
}

// 优化标题
const handleOptimize = async () => {
  if (!form.originalTitle.trim()) {
    ElMessage.warning('请输入要优化的标题')
    return
  }

  loading.value = true
  analyzeResult.value = null
  optimizeResult.value = null

  try {
    const result = await optimizeTitle({
      original_title: form.originalTitle,
      platform: form.platform,
    })
    optimizeResult.value = result
  } catch (error: any) {
    ElMessage.error(error.message || '标题优化失败，请重试')
  } finally {
    loading.value = false
  }
}

// 分析标题
const handleAnalyze = async () => {
  if (!form.originalTitle.trim()) {
    ElMessage.warning('请输入要分析的标题')
    return
  }

  analyzing.value = true
  analyzeResult.value = null
  optimizeResult.value = null

  try {
    const result = await analyzeTitle({
      title: form.originalTitle,
      platform: form.platform,
    })
    analyzeResult.value = result
  } catch (error: any) {
    ElMessage.error(error.message || '标题分析失败，请重试')
  } finally {
    analyzing.value = false
  }
}

// 选择标题
const selectTitle = (item: { title: string }) => {
  selectedTitle.value = item.title
  emit('select', item.title)
}

// 暴露方法
defineExpose({
  setTitle: (title: string) => {
    form.originalTitle = title
  },
})
</script>

<style scoped lang="scss">
.title-optimizer {
  .optimizer-card {
    border-radius: 12px;
  }

  .card-header {
    display: flex;
    align-items: center;
    gap: 8px;

    .title {
      display: flex;
      align-items: center;
      gap: 6px;
      font-weight: 600;
      font-size: 16px;
    }

    .help-icon {
      color: #909399;
      cursor: help;
    }
  }

  .el-form-item {
    margin-bottom: 16px;
  }

  .analyze-result {
    margin-top: 20px;
    padding-top: 20px;
    border-top: 1px solid #ebeef5;

    .score-section {
      display: flex;
      align-items: center;
      gap: 20px;
      margin-bottom: 20px;

      .score-circle {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        background: linear-gradient(135deg, var(--score-color), color-mix(in srgb, var(--score-color) 70%, white));
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        color: white;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);

        .score-value {
          font-size: 28px;
          font-weight: 700;
          line-height: 1;
        }

        .score-label {
          font-size: 10px;
          opacity: 0.9;
        }
      }

      .score-info {
        .style-info {
          margin-top: 8px;
          color: #606266;
          font-size: 14px;
        }
      }
    }

    .feedback-list {
      list-style: none;
      padding: 0;
      margin: 0;

      li {
        display: flex;
        align-items: flex-start;
        gap: 8px;
        padding: 8px 0;
        font-size: 14px;
        color: #606266;

        .el-icon {
          margin-top: 2px;
          flex-shrink: 0;
        }
      }

      &.strengths .el-icon {
        color: #67c23a;
      }

      &.weaknesses .el-icon {
        color: #e6a23c;
      }

      &.suggestions .el-icon {
        color: #409eff;
      }
    }
  }

  .optimize-result {
    margin-top: 20px;
    padding-top: 20px;
    border-top: 1px solid #ebeef5;

    .original-analysis {
      background: #fafafa;
      padding: 16px;
      border-radius: 8px;
      margin-bottom: 16px;

      h4 {
        margin: 0 0 12px;
        font-size: 14px;
        color: #303133;
      }

      .original-score {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 12px;
        font-size: 14px;
      }

      .issues {
        p {
          margin: 0 0 8px;
          font-size: 14px;
          color: #606266;
        }

        ul {
          margin: 0;
          padding-left: 20px;

          li {
            font-size: 13px;
            color: #909399;
            margin-bottom: 4px;
          }
        }
      }
    }

    .optimized-titles {
      display: flex;
      flex-direction: column;
      gap: 12px;

      .title-item {
        padding: 16px;
        border: 1px solid #e4e7ed;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.2s;

        &:hover {
          border-color: #409eff;
          box-shadow: 0 2px 8px rgba(64, 158, 255, 0.15);
        }

        &.selected {
          border-color: #409eff;
          background: rgba(64, 158, 255, 0.05);
        }

        .title-content {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          gap: 12px;
          margin-bottom: 8px;

          .title-text {
            font-size: 15px;
            color: #303133;
            font-weight: 500;
            flex: 1;
          }

          .title-meta {
            display: flex;
            gap: 6px;
            flex-shrink: 0;
          }
        }

        .title-hooks {
          display: flex;
          flex-wrap: wrap;
          gap: 6px;
          margin-bottom: 8px;
        }

        .title-explanation {
          margin: 0;
          font-size: 13px;
          color: #909399;
          line-height: 1.5;
        }
      }
    }

    .improvement-tips {
      margin-top: 20px;
      padding: 16px;
      background: #f0f9eb;
      border-radius: 8px;

      h4 {
        margin: 0 0 12px;
        font-size: 14px;
        color: #67c23a;
      }

      ul {
        margin: 0;
        padding-left: 20px;

        li {
          font-size: 13px;
          color: #606266;
          margin-bottom: 6px;
        }
      }
    }
  }
}
</style>
