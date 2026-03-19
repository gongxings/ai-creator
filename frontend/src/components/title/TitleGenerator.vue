<template>
  <div class="title-generator">
    <el-card class="generator-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span class="title">
            <el-icon><Edit /></el-icon>
            爆款标题生成器
          </span>
          <el-tooltip content="输入内容主题，AI 自动生成多个高点击率标题">
            <el-icon class="help-icon"><QuestionFilled /></el-icon>
          </el-tooltip>
        </div>
      </template>

      <el-form :model="form" label-position="top">
        <el-form-item label="内容主题/摘要">
          <el-input
            v-model="form.content"
            type="textarea"
            :rows="3"
            placeholder="输入您的内容主题或摘要，例如：分享三个提高工作效率的方法"
            :maxlength="500"
            show-word-limit
          />
        </el-form-item>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="目标平台">
              <el-select v-model="form.platform" placeholder="选择平台（可选）" clearable>
                <el-option
                  v-for="p in platforms"
                  :key="p.value"
                  :label="p.label"
                  :value="p.value"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="标题风格">
              <el-select v-model="form.style" placeholder="选择风格（可选）" clearable>
                <el-option
                  v-for="s in styles"
                  :key="s.value"
                  :label="s.label"
                  :value="s.value"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="必须包含的关键词">
          <el-select
            v-model="form.keywords"
            multiple
            filterable
            allow-create
            default-first-option
            placeholder="输入关键词后按回车添加（可选）"
          />
        </el-form-item>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="生成数量">
              <el-slider v-model="form.count" :min="1" :max="10" :step="1" show-input />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="语气">
              <el-select v-model="form.tone" placeholder="选择语气（可选）" clearable>
                <el-option label="专业严谨" value="专业" />
                <el-option label="轻松活泼" value="轻松" />
                <el-option label="幽默风趣" value="幽默" />
                <el-option label="正式严肃" value="严肃" />
                <el-option label="亲切温暖" value="亲切" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            :disabled="!form.content.trim()"
            @click="handleGenerate"
          >
            <el-icon><MagicStick /></el-icon>
            生成爆款标题
          </el-button>
        </el-form-item>
      </el-form>

      <!-- 生成结果 -->
      <div v-if="result" class="generate-result">
        <el-divider>生成结果</el-divider>

        <div class="titles-grid">
          <div
            v-for="(item, idx) in result.titles"
            :key="idx"
            class="title-item"
            :class="{ selected: selectedTitle === item.title }"
            @click="selectTitle(item)"
          >
            <div class="title-header">
              <span class="rank">#{{ idx + 1 }}</span>
              <div class="score-badge" :style="{ backgroundColor: getScoreColor(item.score) }">
                {{ item.score }}分
              </div>
            </div>
            <h4 class="title-text">{{ item.title }}</h4>
            <div class="title-meta">
              <el-tag size="small" type="info">{{ STYLE_LABELS[item.style] || item.style }}</el-tag>
              <el-tag
                v-for="hook in item.hooks.slice(0, 3)"
                :key="hook"
                size="small"
                type="warning"
              >
                {{ hook }}
              </el-tag>
            </div>
            <p v-if="item.explanation" class="explanation">{{ item.explanation }}</p>
            <div class="title-actions">
              <el-button size="small" text type="primary" @click.stop="copyTitle(item.title)">
                <el-icon><CopyDocument /></el-icon>
                复制
              </el-button>
              <el-button size="small" text type="success" @click.stop="useTitle(item.title)">
                <el-icon><Check /></el-icon>
                使用此标题
              </el-button>
            </div>
          </div>
        </div>

        <div v-if="result.analysis" class="analysis-tip">
          <el-icon><InfoFilled /></el-icon>
          <span>{{ result.analysis }}</span>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import {
  Edit,
  QuestionFilled,
  MagicStick,
  CopyDocument,
  Check,
  InfoFilled,
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import {
  generateTitles,
  PlatformType,
  TitleStyle,
  STYLE_LABELS,
  getScoreColor,
  type TitleGenerateResponse,
} from '@/api/title'

// Emits
const emit = defineEmits<{
  (e: 'select', title: string): void
}>()

// 状态
const loading = ref(false)
const result = ref<TitleGenerateResponse | null>(null)
const selectedTitle = ref('')

// 表单数据
const form = reactive({
  content: '',
  platform: undefined as PlatformType | undefined,
  style: undefined as TitleStyle | undefined,
  keywords: [] as string[],
  count: 5,
  tone: undefined as string | undefined,
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

// 风格选项
const styles = [
  { value: TitleStyle.CURIOSITY, label: '好奇心驱动 - 制造悬念' },
  { value: TitleStyle.BENEFIT, label: '利益驱动 - 突出价值' },
  { value: TitleStyle.EMOTIONAL, label: '情感驱动 - 引发共鸣' },
  { value: TitleStyle.TRENDING, label: '热点借势 - 蹭热度' },
  { value: TitleStyle.LISTICLE, label: '数字清单 - 量化价值' },
  { value: TitleStyle.QUESTION, label: '提问式 - 引发思考' },
  { value: TitleStyle.HOW_TO, label: '教程式 - 提供方案' },
  { value: TitleStyle.CONTRAST, label: '对比反差 - 制造冲突' },
]

// 生成标题
const handleGenerate = async () => {
  if (!form.content.trim()) {
    ElMessage.warning('请输入内容主题或摘要')
    return
  }

  loading.value = true
  result.value = null

  try {
    const response = await generateTitles({
      content: form.content,
      platform: form.platform,
      style: form.style,
      keywords: form.keywords.length > 0 ? form.keywords : undefined,
      count: form.count,
      tone: form.tone,
    })
    result.value = response
  } catch (error: any) {
    ElMessage.error(error.message || '标题生成失败，请重试')
  } finally {
    loading.value = false
  }
}

// 选择标题
const selectTitle = (item: { title: string }) => {
  selectedTitle.value = item.title
  emit('select', item.title)
}

// 复制标题
const copyTitle = async (title: string) => {
  try {
    await navigator.clipboard.writeText(title)
    ElMessage.success('已复制到剪贴板')
  } catch {
    ElMessage.error('复制失败')
  }
}

// 使用标题
const useTitle = (title: string) => {
  selectedTitle.value = title
  emit('select', title)
  ElMessage.success('已选择此标题')
}

// 暴露方法
defineExpose({
  setContent: (content: string) => {
    form.content = content
  },
})
</script>

<style scoped lang="scss">
.title-generator {
  .generator-card {
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

  .generate-result {
    margin-top: 20px;

    .titles-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
      gap: 16px;

      .title-item {
        padding: 16px;
        border: 1px solid #e4e7ed;
        border-radius: 12px;
        cursor: pointer;
        transition: all 0.2s;
        background: #fff;

        &:hover {
          border-color: #409eff;
          box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
          transform: translateY(-2px);
        }

        &.selected {
          border-color: #409eff;
          background: linear-gradient(135deg, rgba(64, 158, 255, 0.05), rgba(64, 158, 255, 0.02));
        }

        .title-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 12px;

          .rank {
            font-size: 14px;
            font-weight: 600;
            color: #909399;
          }

          .score-badge {
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 600;
            color: white;
          }
        }

        .title-text {
          margin: 0 0 12px;
          font-size: 15px;
          font-weight: 500;
          color: #303133;
          line-height: 1.5;
        }

        .title-meta {
          display: flex;
          flex-wrap: wrap;
          gap: 6px;
          margin-bottom: 10px;
        }

        .explanation {
          margin: 0 0 12px;
          font-size: 13px;
          color: #909399;
          line-height: 1.5;
        }

        .title-actions {
          display: flex;
          gap: 8px;
          padding-top: 12px;
          border-top: 1px solid #f0f0f0;
        }
      }
    }

    .analysis-tip {
      display: flex;
      align-items: flex-start;
      gap: 8px;
      margin-top: 20px;
      padding: 14px 16px;
      background: linear-gradient(135deg, #e6f7ff, #f0f5ff);
      border-radius: 8px;
      font-size: 14px;
      color: #1890ff;

      .el-icon {
        margin-top: 2px;
        flex-shrink: 0;
      }
    }
  }
}
</style>
