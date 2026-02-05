<template>
  <div class="writing-editor">
    <div class="editor-hero">
      <h1>{{ toolInfo.name }}</h1>
      <p>{{ toolInfo.description }}</p>
    </div>

    <el-card class="editor-card">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-button type="text" :icon="ArrowLeft" @click="router.back()">返回</el-button>
            <el-divider direction="vertical" />
            <h2>{{ toolInfo.name }}</h2>
          </div>
          <div class="header-right">
            <el-button v-if="currentCreation" type="primary" :icon="Upload" @click="showPublishDialog = true">发布</el-button>
          </div>
        </div>
      </template>

      <el-row :gutter="24">
        <el-col :xs="24" :lg="10">
          <div class="input-section">
            <h3>输入信息</h3>
            <el-form ref="formRef" :model="formData" label-position="top">
              <el-form-item label="主题" prop="topic">
                <el-input v-model="formData.topic" placeholder="请输入创作主题" />
              </el-form-item>
              <el-form-item label="关键词">
                <el-input v-model="formData.keywords" placeholder="多个关键词用逗号分隔" />
              </el-form-item>
              <el-form-item label="风格">
                <el-select v-model="formData.style" placeholder="选择风格" style="width: 100%">
                  <el-option label="专业严谨" value="professional" />
                  <el-option label="轻松幽默" value="humorous" />
                  <el-option label="情感共鸣" value="emotional" />
                </el-select>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" :loading="generating" @click="handleGenerate" style="width: 100%">
                  <el-icon v-if="!generating"><MagicStick /></el-icon>
                  {{ generating ? '生成中...' : '一键生成' }}
                </el-button>
              </el-form-item>
            </el-form>

            <el-card shadow="never" class="model-card">
              <template #header><span>AI模型</span></template>
              <el-select v-model="selectedModel" placeholder="选择AI模型" style="width: 100%">
                <el-option v-for="model in aiModels" :key="model.id" :label="`${model.name} (${model.provider})`" :value="model.id" />
              </el-select>
            </el-card>

            <div class="tips-card">
              <h4>创作建议</h4>
              <ul>
                <li>主题尽量具体，能提升生成质量。</li>
                <li>关键词建议 3~6 个，帮助模型聚焦。</li>
                <li>完成后可用“优化”进一步提升可读性。</li>
              </ul>
            </div>
          </div>
        </el-col>

        <el-col :xs="24" :lg="14">
          <div class="preview-section">
            <div class="preview-header">
              <h3>内容预览</h3>
              <div class="preview-meta" v-if="currentCreation">
                <el-tag size="small" effect="plain">字数：{{ contentStats.wordCount }}</el-tag>
                <el-tag size="small" effect="plain">预计阅读：{{ contentStats.readingMinutes }} 分钟</el-tag>
              </div>
              <div class="preview-actions">
                <el-button v-if="currentCreation" :icon="RefreshRight" @click="handleRegenerate" :loading="generating">重新生成</el-button>
                <el-button v-if="currentCreation" :icon="MagicStick" @click="showOptimizeDialog = true">优化</el-button>
                <el-button v-if="currentCreation" :icon="Download" @click="handleExport">导出</el-button>
              </div>
            </div>
            <div v-if="!currentCreation" class="empty-preview">
              <el-empty description="请填写信息并点击生成按钮" />
            </div>
            <div v-else class="content-preview">
              <div ref="editorRef" class="editor-container"></div>
            </div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <el-dialog v-model="showOptimizeDialog" title="内容优化" width="500px">
      <el-form label-position="top">
        <el-form-item label="优化类型">
          <el-checkbox-group v-model="optimizeTypes">
            <el-checkbox label="seo">SEO优化</el-checkbox>
            <el-checkbox label="readability">可读性</el-checkbox>
            <el-checkbox label="style">文风</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showOptimizeDialog = false">取消</el-button>
        <el-button type="primary" :loading="optimizing" @click="handleOptimize">开始优化</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showPublishDialog" title="发布内容" width="600px">
      <el-form label-position="top">
        <el-form-item label="选择平台">
          <el-checkbox-group v-model="selectedPlatforms">
            <el-checkbox label="wechat">微信公众号</el-checkbox>
            <el-checkbox label="xiaohongshu">小红书</el-checkbox>
            <el-checkbox label="douyin">抖音</el-checkbox>
            <el-checkbox label="toutiao">今日头条</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showPublishDialog = false">取消</el-button>
        <el-button type="primary" :loading="publishing" @click="handlePublish">确认发布</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Upload, RefreshRight, MagicStick, Download } from '@element-plus/icons-vue'
import Quill from 'quill'
import 'quill/dist/quill.snow.css'
import { generateContent, regenerateContent, optimizeContent } from '@/api/writing'
import { publishContent } from '@/api/publish'
import { getAIModels } from '@/api/models'
import type { Creation, AIModel } from '@/types'

const router = useRouter()
const route = useRoute()
const toolType = computed(() => route.params.toolType as string)

const toolMetaMap: Record<string, { name: string; description: string }> = {
  wechat_article: { name: '公众号文章', description: '面向微信生态，突出可读性与传播性。' },
  xiaohongshu_note: { name: '小红书笔记', description: '适合种草与经验分享，强调标题吸引力。' },
  official_document: { name: '公文写作', description: '结构规范、语气正式，适用于公文场景。' },
  academic_paper: { name: '论文写作', description: '提供学术风格文本草稿，便于继续完善。' },
  marketing_copy: { name: '营销文案', description: '强化卖点表达，提升转化效率。' },
  news_article: { name: '新闻稿/软文', description: '兼顾信息传递与品牌表达。' },
  video_script: { name: '短视频脚本', description: '快速生成结构化脚本与镜头节奏。' },
  story_novel: { name: '故事/小说', description: '激发创意叙事，搭建情节框架。' },
  business_plan: { name: '商业计划书', description: '输出商业方案初稿与关键模块。' },
  work_report: { name: '工作报告', description: '提炼工作成果，形成清晰报告结构。' },
  resume: { name: '简历/求职信', description: '突出优势与匹配度，提升表达质量。' },
  lesson_plan: { name: '教案/课件', description: '生成教学目标清晰的内容骨架。' },
  content_rewrite: { name: '改写/扩写/缩写', description: '对既有内容进行定向优化与重构。' },
  translation: { name: '多语言翻译', description: '保留语义与风格的一致性表达。' },
}

const toolInfo = computed(() => toolMetaMap[toolType.value] || { name: 'AI写作工具', description: '智能生成高质量写作内容。' })

const formRef = ref()
const formData = reactive({ topic: '', keywords: '', style: 'professional' })
const aiModels = ref<AIModel[]>([])
const selectedModel = ref<number>()
const editorRef = ref<HTMLElement>()
let quillEditor: Quill | null = null
const currentCreation = ref<Creation>()
const generating = ref(false)
const optimizing = ref(false)
const publishing = ref(false)
const showOptimizeDialog = ref(false)
const showPublishDialog = ref(false)
const optimizeTypes = ref<string[]>([])
const selectedPlatforms = ref<string[]>([])

const contentStats = computed(() => {
  const text = quillEditor?.getText()?.trim() || currentCreation.value?.content?.replace(/<[^>]*>/g, '').trim() || ''
  const wordCount = text.replace(/\s+/g, '').length
  const readingMinutes = Math.max(1, Math.ceil(wordCount / 300))
  return { wordCount, readingMinutes }
})

const initEditor = () => {
  if (editorRef.value && !quillEditor) {
    quillEditor = new Quill(editorRef.value, {
      theme: 'snow',
      modules: {
        toolbar: [
          [{ header: [1, 2, 3, false] }],
          ['bold', 'italic', 'underline'],
          [{ list: 'ordered' }, { list: 'bullet' }],
          ['link', 'image'],
          ['clean']
        ]
      }
    })
  }
}

const handleGenerate = async () => {
  if (!formData.topic) {
    ElMessage.warning('请输入主题')
    return
  }
  generating.value = true
  try {
    const res = await generateContent(toolType.value, {
      ...formData,
      model_id: selectedModel.value
    })
    currentCreation.value = res
    if (quillEditor) {
      quillEditor.root.innerHTML = res.content
    }
    ElMessage.success('生成成功')
  } catch (error: any) {
    ElMessage.error(error.message || '生成失败')
  } finally {
    generating.value = false
  }
}

const handleRegenerate = async () => {
  if (!currentCreation.value) return
  generating.value = true
  try {
    const res = await regenerateContent(currentCreation.value.id)
    currentCreation.value = res
    if (quillEditor) {
      quillEditor.root.innerHTML = res.content
    }
    ElMessage.success('重新生成成功')
  } catch (error: any) {
    ElMessage.error(error.message || '重新生成失败')
  } finally {
    generating.value = false
  }
}

const handleOptimize = async () => {
  if (!currentCreation.value || optimizeTypes.value.length === 0) {
    ElMessage.warning('请选择优化类型')
    return
  }
  optimizing.value = true
  try {
    const res = await optimizeContent(currentCreation.value.id, {
      optimize_types: optimizeTypes.value
    })
    currentCreation.value = res
    if (quillEditor) {
      quillEditor.root.innerHTML = res.content
    }
    showOptimizeDialog.value = false
    ElMessage.success('优化成功')
  } catch (error: any) {
    ElMessage.error(error.message || '优化失败')
  } finally {
    optimizing.value = false
  }
}

const handlePublish = async () => {
  if (!currentCreation.value || selectedPlatforms.value.length === 0) {
    ElMessage.warning('请选择发布平台')
    return
  }
  publishing.value = true
  try {
    await publishContent({
      creation_id: currentCreation.value.id,
      platforms: selectedPlatforms.value
    })
    showPublishDialog.value = false
    selectedPlatforms.value = []
    ElMessage.success('发布成功')
  } catch (error: any) {
    ElMessage.error(error.message || '发布失败')
  } finally {
    publishing.value = false
  }
}

const handleExport = () => {
  if (!currentCreation.value) return
  const htmlContent = quillEditor?.root?.innerHTML || currentCreation.value.content
  const blob = new Blob([htmlContent], { type: 'text/html' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${currentCreation.value.title || '内容'}.html`
  a.click()
  URL.revokeObjectURL(url)
}

const loadModels = async () => {
  try {
    const res = await getAIModels()
    aiModels.value = res
    if (aiModels.value.length > 0) {
      selectedModel.value = aiModels.value[0].id
    }
  } catch (error: any) {
    ElMessage.error(error.message || '加载模型失败')
  }
}

onMounted(() => {
  initEditor()
  loadModels()
})
</script>

<style scoped lang="scss">
.writing-editor {
  display: flex;
  flex-direction: column;
  gap: 16px;
  background: linear-gradient(180deg, #f8fbff 0%, #ffffff 36%);

  .editor-hero {
    padding: 22px 24px;
    border-radius: 14px;
    background: linear-gradient(135deg, #eff6ff 0%, #f5f3ff 100%);

    h1 {
      margin: 0 0 8px;
      font-size: 26px;
      color: #1f2937;
    }

    p {
      margin: 0;
      color: #64748b;
    }
  }

  :deep(.el-card) {
    border-radius: 14px;
    border: 1px solid #edf2f7;
    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.04);
  }

  .editor-card {
    :deep(.el-card__header) {
      padding: 16px 24px;
    }

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;

      .header-left {
        display: flex;
        align-items: center;
        gap: 12px;

        h2 {
          margin: 0;
          font-size: 20px;
          font-weight: 600;
          color: #1f2937;
        }
      }
    }
  }

  .input-section {
    h3 {
      margin-bottom: 16px;
      font-size: 16px;
      font-weight: 600;
      color: #1f2937;
    }

    .model-card {
      margin-top: 20px;
    }

    .tips-card {
      margin-top: 16px;
      padding: 14px 16px;
      border: 1px solid #e5e7eb;
      border-radius: 12px;
      background: #f8fafc;

      h4 {
        margin: 0 0 8px;
        color: #334155;
        font-size: 14px;
      }

      ul {
        margin: 0;
        padding-left: 18px;
        color: #64748b;
        font-size: 13px;
        line-height: 1.7;
      }
    }
  }

  .preview-section {
    .preview-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 10px;
      margin-bottom: 16px;

      h3 {
        margin: 0;
        font-size: 16px;
        font-weight: 600;
        color: #1f2937;
      }

      .preview-meta {
        display: flex;
        gap: 8px;
      }

      .preview-actions {
        display: flex;
        gap: 8px;
      }
    }

    .empty-preview {
      min-height: 400px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: #f8fafc;
      border-radius: 10px;
      border: 1px dashed #dbe3ef;
    }

    .content-preview {
      .editor-container {
        min-height: 500px;
        background: #fff;
        border: 1px solid #dbe3ef;
        border-radius: 10px;

        :deep(.ql-toolbar.ql-snow) {
          border: none;
          border-bottom: 1px solid #e5e7eb;
          border-radius: 10px 10px 0 0;
        }

        :deep(.ql-container) {
          min-height: 450px;
          font-size: 14px;
          border: none;
        }

        :deep(.ql-editor) {
          min-height: 450px;
          line-height: 1.75;
        }
      }
    }
  }
}

@media (max-width: 992px) {
  .writing-editor {
    .editor-hero {
      padding: 18px;

      h1 {
        font-size: 22px;
      }
    }

    .input-section {
      margin-bottom: 24px;
    }
  }
}
</style>
