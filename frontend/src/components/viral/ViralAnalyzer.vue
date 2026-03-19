<template>
  <div class="viral-analyzer">
    <el-tabs v-model="activeTab" type="border-card">
      <!-- 爆款分析 Tab -->
      <el-tab-pane label="爆款分析" name="analyze">
        <el-card class="analyzer-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span class="title">
                <el-icon><TrendCharts /></el-icon>
                分析爆款内容
              </span>
              <el-tooltip content="深度分析爆款文章的成功要素，提取可复用的写作技巧">
                <el-icon class="help-icon"><QuestionFilled /></el-icon>
              </el-tooltip>
            </div>
          </template>

          <el-form :model="analyzeForm" label-position="top">
            <el-form-item label="爆款内容">
              <el-input
                v-model="analyzeForm.content"
                type="textarea"
                :rows="8"
                placeholder="粘贴一篇爆款文章的正文内容（至少50字）"
                :maxlength="20000"
                show-word-limit
              />
            </el-form-item>

            <el-row :gutter="16">
              <el-col :span="12">
                <el-form-item label="文章标题（可选）">
                  <el-input
                    v-model="analyzeForm.title"
                    placeholder="输入文章标题"
                    :maxlength="100"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="来源平台（可选）">
                  <el-select v-model="analyzeForm.platform" placeholder="选择来源平台" clearable>
                    <el-option label="微信公众号" value="wechat" />
                    <el-option label="小红书" value="xiaohongshu" />
                    <el-option label="抖音" value="douyin" />
                    <el-option label="知乎" value="zhihu" />
                    <el-option label="微博" value="weibo" />
                    <el-option label="今日头条" value="toutiao" />
                    <el-option label="B站" value="bilibili" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item>
              <el-button
                type="primary"
                size="large"
                :loading="analyzeLoading"
                :disabled="analyzeForm.content.length < 50"
                @click="handleAnalyze"
              >
                <el-icon><DataAnalysis /></el-icon>
                开始分析
              </el-button>
            </el-form-item>
          </el-form>

          <!-- 分析结果 -->
          <div v-if="analyzeResult" class="analyze-result">
            <el-divider>分析报告</el-divider>

            <!-- 概览 -->
            <div class="result-overview">
              <div class="overview-item score">
                <div class="score-circle" :style="{ borderColor: getViralScoreColor(analyzeResult.viral_score) }">
                  <span class="score-value">{{ analyzeResult.viral_score }}</span>
                  <span class="score-label">爆款指数</span>
                </div>
              </div>
              <div class="overview-item info">
                <div class="info-row">
                  <span class="label">内容类别：</span>
                  <el-tag :color="CATEGORY_COLORS[analyzeResult.category]" effect="dark">
                    {{ CATEGORY_LABELS[analyzeResult.category] }}
                  </el-tag>
                </div>
                <div class="info-row">
                  <span class="label">语气风格：</span>
                  <span>{{ analyzeResult.tone }}</span>
                </div>
                <div class="info-row">
                  <span class="label">目标受众：</span>
                  <span>{{ analyzeResult.target_audience }}</span>
                </div>
              </div>
            </div>

            <!-- 爆款元素 -->
            <div class="result-section">
              <h4 class="section-title">
                <el-icon><Star /></el-icon>
                爆款元素分析
              </h4>
              <div class="elements-grid">
                <div
                  v-for="element in analyzeResult.viral_elements"
                  :key="element.name"
                  class="element-card"
                >
                  <div class="element-header">
                    <span class="element-name">{{ element.name }}</span>
                    <el-progress
                      :percentage="element.score"
                      :stroke-width="8"
                      :color="getViralScoreColor(element.score)"
                      :show-text="false"
                      style="width: 100px"
                    />
                    <span class="element-score">{{ element.score }}分</span>
                  </div>
                  <p class="element-desc">{{ element.description }}</p>
                  <div v-if="element.examples.length > 0" class="element-examples">
                    <span class="examples-label">示例：</span>
                    <el-tag v-for="(ex, i) in element.examples.slice(0, 2)" :key="i" size="small" type="info">
                      {{ ex.slice(0, 30) }}{{ ex.length > 30 ? '...' : '' }}
                    </el-tag>
                  </div>
                </div>
              </div>
            </div>

            <!-- 情感触发点 -->
            <div class="result-section">
              <h4 class="section-title">
                <el-icon><Promotion /></el-icon>
                情感触发点
              </h4>
              <div class="tags-list">
                <el-tag
                  v-for="trigger in analyzeResult.emotional_triggers"
                  :key="trigger"
                  type="danger"
                  effect="plain"
                >
                  {{ trigger }}
                </el-tag>
              </div>
            </div>

            <!-- 写作技巧 -->
            <div class="result-section">
              <h4 class="section-title">
                <el-icon><Edit /></el-icon>
                写作技巧
              </h4>
              <div class="tags-list">
                <el-tag
                  v-for="tech in analyzeResult.writing_techniques"
                  :key="tech"
                  type="success"
                  effect="plain"
                >
                  {{ tech }}
                </el-tag>
              </div>
            </div>

            <!-- 结构分析 -->
            <div class="result-section">
              <h4 class="section-title">
                <el-icon><List /></el-icon>
                结构分析
              </h4>
              <el-descriptions :column="1" border>
                <el-descriptions-item label="开头钩子">
                  {{ analyzeResult.structure.opening_hook }}
                </el-descriptions-item>
                <el-descriptions-item label="结尾CTA">
                  {{ analyzeResult.structure.closing_cta }}
                </el-descriptions-item>
                <el-descriptions-item label="过渡风格">
                  {{ analyzeResult.structure.transition_style }}
                </el-descriptions-item>
              </el-descriptions>
            </div>

            <!-- 改进建议 -->
            <div v-if="analyzeResult.improvement_suggestions.length > 0" class="result-section">
              <h4 class="section-title">
                <el-icon><Warning /></el-icon>
                可改进的点
              </h4>
              <ul class="suggestions-list">
                <li v-for="(sug, i) in analyzeResult.improvement_suggestions" :key="i">
                  {{ sug }}
                </li>
              </ul>
            </div>

            <!-- 操作按钮 -->
            <div class="result-actions">
              <el-button type="primary" @click="useForImitate">
                <el-icon><CopyDocument /></el-icon>
                用此文章作为模仿参考
              </el-button>
            </div>
          </div>
        </el-card>
      </el-tab-pane>

      <!-- 爆款模仿 Tab -->
      <el-tab-pane label="爆款模仿" name="imitate">
        <el-card class="imitate-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span class="title">
                <el-icon><MagicStick /></el-icon>
                模仿爆款生成
              </span>
              <el-tooltip content="参考爆款文章的风格，围绕新主题创作类似内容">
                <el-icon class="help-icon"><QuestionFilled /></el-icon>
              </el-tooltip>
            </div>
          </template>

          <el-form :model="imitateForm" label-position="top">
            <el-form-item label="参考爆款内容">
              <el-input
                v-model="imitateForm.reference_content"
                type="textarea"
                :rows="6"
                placeholder="粘贴你想模仿的爆款文章内容（至少50字）"
                :maxlength="20000"
                show-word-limit
              />
            </el-form-item>

            <el-form-item label="参考标题（可选）">
              <el-input
                v-model="imitateForm.reference_title"
                placeholder="输入参考文章的标题"
                :maxlength="100"
              />
            </el-form-item>

            <el-form-item label="新主题">
              <el-input
                v-model="imitateForm.new_topic"
                placeholder="输入你想写的新主题，例如：如何高效学习英语"
                :maxlength="200"
              />
            </el-form-item>

            <el-row :gutter="16">
              <el-col :span="12">
                <el-form-item label="目标平台（可选）">
                  <el-select v-model="imitateForm.platform" placeholder="选择目标平台" clearable>
                    <el-option label="微信公众号" value="wechat" />
                    <el-option label="小红书" value="xiaohongshu" />
                    <el-option label="抖音" value="douyin" />
                    <el-option label="知乎" value="zhihu" />
                    <el-option label="微博" value="weibo" />
                    <el-option label="今日头条" value="toutiao" />
                    <el-option label="B站" value="bilibili" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="风格模仿强度">
                  <el-slider
                    v-model="imitateForm.style_strength"
                    :min="0"
                    :max="100"
                    :step="10"
                    :marks="{ 0: '原创', 50: '适中', 100: '高度模仿' }"
                  />
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item>
              <el-checkbox v-model="imitateForm.keep_structure">保持相同的文章结构</el-checkbox>
            </el-form-item>

            <el-form-item label="额外要求（可选）">
              <el-input
                v-model="imitateForm.additional_requirements"
                type="textarea"
                :rows="2"
                placeholder="例如：语气更轻松一些，字数控制在1000字左右"
              />
            </el-form-item>

            <el-form-item>
              <el-button
                type="primary"
                size="large"
                :loading="imitateLoading"
                :disabled="imitateForm.reference_content.length < 50 || !imitateForm.new_topic.trim()"
                @click="handleImitate"
              >
                <el-icon><MagicStick /></el-icon>
                生成模仿内容
              </el-button>
            </el-form-item>
          </el-form>

          <!-- 模仿结果 -->
          <div v-if="imitateResult" class="imitate-result">
            <el-divider>生成结果</el-divider>

            <div class="result-header">
              <h3 class="result-title">{{ imitateResult.title }}</h3>
              <div class="result-meta">
                <span>
                  <el-icon><Document /></el-icon>
                  {{ imitateResult.word_count }} 字
                </span>
                <span>
                  <el-icon><TrendCharts /></el-icon>
                  预估爆款指数：
                  <em :style="{ color: getViralScoreColor(imitateResult.estimated_viral_score) }">
                    {{ imitateResult.estimated_viral_score }}
                  </em>
                </span>
              </div>
            </div>

            <div class="result-content">
              <pre class="content-text">{{ imitateResult.content }}</pre>
            </div>

            <div v-if="imitateResult.elements_applied.length > 0" class="result-elements">
              <span class="label">应用的爆款元素：</span>
              <el-tag
                v-for="elem in imitateResult.elements_applied"
                :key="elem"
                type="warning"
                effect="plain"
              >
                {{ elem }}
              </el-tag>
            </div>

            <div v-if="imitateResult.imitation_notes.length > 0" class="result-notes">
              <el-collapse>
                <el-collapse-item title="模仿说明">
                  <ul>
                    <li v-for="(note, i) in imitateResult.imitation_notes" :key="i">{{ note }}</li>
                  </ul>
                </el-collapse-item>
              </el-collapse>
            </div>

            <div class="result-actions">
              <el-button type="primary" @click="copyImitateResult">
                <el-icon><CopyDocument /></el-icon>
                复制内容
              </el-button>
              <el-button @click="downloadImitateResult">
                <el-icon><Download /></el-icon>
                下载
              </el-button>
              <el-button v-if="imitateResult.creation_id" type="success" @click="viewCreation(imitateResult.creation_id)">
                <el-icon><View /></el-icon>
                查看记录
              </el-button>
            </div>
          </div>
        </el-card>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import {
  TrendCharts,
  QuestionFilled,
  DataAnalysis,
  Star,
  Promotion,
  Edit,
  List,
  Warning,
  CopyDocument,
  MagicStick,
  Document,
  Download,
  View,
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import {
  analyzeContent,
  imitateContent,
  CATEGORY_LABELS,
  CATEGORY_COLORS,
  getViralScoreColor,
  type AnalyzeResponse,
  type ImitateResponse,
} from '@/api/viralAnalyzer'

// Emits
const emit = defineEmits<{
  (e: 'imitated', result: ImitateResponse): void
}>()

const router = useRouter()

// 状态
const activeTab = ref('analyze')
const analyzeLoading = ref(false)
const imitateLoading = ref(false)
const analyzeResult = ref<AnalyzeResponse | null>(null)
const imitateResult = ref<ImitateResponse | null>(null)

// 分析表单
const analyzeForm = reactive({
  content: '',
  title: '',
  platform: '',
})

// 模仿表单
const imitateForm = reactive({
  reference_content: '',
  reference_title: '',
  new_topic: '',
  platform: '',
  style_strength: 80,
  keep_structure: true,
  additional_requirements: '',
})

// 分析爆款内容
const handleAnalyze = async () => {
  if (analyzeForm.content.length < 50) {
    ElMessage.warning('内容至少需要50个字')
    return
  }

  analyzeLoading.value = true
  analyzeResult.value = null

  try {
    const result = await analyzeContent({
      content: analyzeForm.content,
      title: analyzeForm.title || undefined,
      platform: analyzeForm.platform || undefined,
    })
    analyzeResult.value = result
    ElMessage.success('分析完成')
  } catch (error: any) {
    ElMessage.error(error.message || '分析失败，请重试')
  } finally {
    analyzeLoading.value = false
  }
}

// 用分析的内容作为模仿参考
const useForImitate = () => {
  imitateForm.reference_content = analyzeForm.content
  imitateForm.reference_title = analyzeForm.title
  imitateForm.platform = analyzeForm.platform
  activeTab.value = 'imitate'
  ElMessage.success('已复制到模仿面板')
}

// 模仿爆款生成
const handleImitate = async () => {
  if (imitateForm.reference_content.length < 50) {
    ElMessage.warning('参考内容至少需要50个字')
    return
  }
  if (!imitateForm.new_topic.trim()) {
    ElMessage.warning('请输入新主题')
    return
  }

  imitateLoading.value = true
  imitateResult.value = null

  try {
    const result = await imitateContent({
      reference_content: imitateForm.reference_content,
      reference_title: imitateForm.reference_title || undefined,
      new_topic: imitateForm.new_topic,
      platform: imitateForm.platform || undefined,
      style_strength: imitateForm.style_strength,
      keep_structure: imitateForm.keep_structure,
      additional_requirements: imitateForm.additional_requirements || undefined,
    })
    imitateResult.value = result
    emit('imitated', result)
    ElMessage.success('生成完成')
  } catch (error: any) {
    ElMessage.error(error.message || '生成失败，请重试')
  } finally {
    imitateLoading.value = false
  }
}

// 复制模仿结果
const copyImitateResult = async () => {
  if (!imitateResult.value) return
  const text = `${imitateResult.value.title}\n\n${imitateResult.value.content}`
  try {
    await navigator.clipboard.writeText(text)
    ElMessage.success('已复制到剪贴板')
  } catch {
    ElMessage.error('复制失败')
  }
}

// 下载模仿结果
const downloadImitateResult = () => {
  if (!imitateResult.value) return
  const text = `${imitateResult.value.title}\n\n${imitateResult.value.content}`
  const blob = new Blob([text], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${imitateResult.value.title.slice(0, 20)}.txt`
  a.click()
  URL.revokeObjectURL(url)
}

// 查看创作记录
const viewCreation = (creationId: number) => {
  router.push(`/creations/${creationId}`)
}

// 暴露方法
defineExpose({
  setReferenceContent: (content: string, title?: string) => {
    imitateForm.reference_content = content
    if (title) imitateForm.reference_title = title
    activeTab.value = 'imitate'
  },
})
</script>

<style scoped lang="scss">
.viral-analyzer {
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

  .analyze-result,
  .imitate-result {
    margin-top: 20px;
  }

  .result-overview {
    display: flex;
    gap: 32px;
    padding: 24px;
    background: linear-gradient(135deg, #f5f7fa, #fff);
    border-radius: 12px;
    margin-bottom: 24px;

    .overview-item {
      &.score {
        .score-circle {
          width: 120px;
          height: 120px;
          border-radius: 50%;
          border: 6px solid;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          background: #fff;

          .score-value {
            font-size: 36px;
            font-weight: 700;
            color: #303133;
          }

          .score-label {
            font-size: 12px;
            color: #909399;
          }
        }
      }

      &.info {
        flex: 1;
        display: flex;
        flex-direction: column;
        justify-content: center;
        gap: 12px;

        .info-row {
          display: flex;
          align-items: center;
          gap: 8px;

          .label {
            color: #909399;
            min-width: 80px;
          }
        }
      }
    }
  }

  .result-section {
    margin-bottom: 24px;

    .section-title {
      display: flex;
      align-items: center;
      gap: 8px;
      margin: 0 0 16px;
      font-size: 15px;
      font-weight: 600;
      color: #303133;
    }
  }

  .elements-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 16px;

    .element-card {
      padding: 16px;
      background: #f5f7fa;
      border-radius: 8px;

      .element-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 8px;

        .element-name {
          font-weight: 600;
          color: #303133;
        }

        .element-score {
          font-size: 13px;
          color: #909399;
        }
      }

      .element-desc {
        margin: 0 0 8px;
        font-size: 13px;
        color: #606266;
        line-height: 1.5;
      }

      .element-examples {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 6px;

        .examples-label {
          font-size: 12px;
          color: #909399;
        }
      }
    }
  }

  .tags-list {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  .suggestions-list {
    margin: 0;
    padding-left: 20px;

    li {
      font-size: 14px;
      color: #606266;
      line-height: 2;
    }
  }

  .result-actions {
    display: flex;
    gap: 12px;
    padding-top: 20px;
    border-top: 1px solid #ebeef5;
  }

  // 模仿结果样式
  .result-header {
    margin-bottom: 16px;

    .result-title {
      margin: 0 0 12px;
      font-size: 20px;
      font-weight: 600;
      color: #303133;
    }

    .result-meta {
      display: flex;
      gap: 24px;
      font-size: 14px;
      color: #909399;

      span {
        display: flex;
        align-items: center;
        gap: 4px;

        em {
          font-style: normal;
          font-weight: 600;
        }
      }
    }
  }

  .result-content {
    margin-bottom: 16px;

    .content-text {
      margin: 0;
      padding: 20px;
      background: #f5f7fa;
      border-radius: 8px;
      font-size: 14px;
      line-height: 1.8;
      white-space: pre-wrap;
      word-break: break-word;
      font-family: inherit;
      max-height: 500px;
      overflow-y: auto;
    }
  }

  .result-elements {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 8px;
    margin-bottom: 16px;

    .label {
      font-size: 13px;
      color: #909399;
    }
  }

  .result-notes {
    margin-bottom: 16px;

    ul {
      margin: 0;
      padding-left: 20px;

      li {
        font-size: 13px;
        color: #606266;
        line-height: 1.8;
      }
    }
  }
}
</style>
