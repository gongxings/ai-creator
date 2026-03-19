<template>
  <div class="writing-editor">
    <section class="editor-hero">
      <div>
        <p class="eyebrow">Writing Studio</p>
        <h1>{{ toolInfo.name }}</h1>
        <p>{{ toolInfo.description }}</p>
      </div>
    </section>

    <el-card class="editor-card">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-button type="text" :icon="ArrowLeft" @click="router.back()">返回</el-button>
            <el-divider direction="vertical" />
            <h2>{{ toolInfo.name }}</h2>
          </div>
          <div class="header-right">
            <el-button :icon="EditPen" @click="showTitleDialog = true">标题助手</el-button>
            <el-button :icon="Picture" @click="openImagePicker">选择配图</el-button>
            <el-button v-if="currentCreation" type="primary" :icon="Upload" @click="showPublishDialog = true">发布</el-button>
          </div>
        </div>
      </template>

      <el-row :gutter="24">
        <el-col :xs="24" :lg="10">
          <div class="input-section">
            <h3>输入信息</h3>

            <DynamicToolForm ref="dynamicFormRef" :tool-type="toolType" v-model="formData" />

            <div class="generate-block">
              <el-button type="primary" :loading="generating" @click="handleGenerate" class="generate-button">
                <el-icon v-if="!generating"><MagicStick /></el-icon>
                {{ generating ? '生成中...' : '一键生成' }}
              </el-button>
            </div>

            <el-card shadow="never" class="side-card model-card">
              <template #header><span>AI 服务</span></template>

              <el-form-item label="选择模型" prop="selectedModel">
                <el-select v-model="selectedModel" placeholder="选择 AI 模型" style="width: 100%">
                  <el-option v-for="model in aiModels" :key="model.id" :label="`${model.name} (${model.provider})`" :value="model.id" />
                </el-select>
              </el-form-item>
              <el-alert type="info" title="API Key 模式说明" :closable="false">
                <p>使用已配置的 API Key 调用官方接口时，通常会消耗积分。</p>
              </el-alert>
            </el-card>

            <el-card shadow="never" class="side-card plugin-card">
              <template #header>
                <div class="plugin-header">
                  <span>创作插件</span>
                  <el-button link type="primary" size="small" @click="router.push('/plugins/market')">管理插件</el-button>
                </div>
              </template>
              <div class="plugin-selector-wrapper">
                <PluginSelector v-model="selectedPlugins" :tool-type="toolType" @change="onPluginSelectionChange" />
                <span class="plugin-hint">
                  {{ selectedPlugins.length > 0 ? `已选择 ${selectedPlugins.length} 个插件` : '启用插件后可补充实时信息与外部能力' }}
                </span>
              </div>
              <el-alert v-if="selectedPlugins.length > 0" type="success" :closable="false" class="plugin-alert">
                <p>生成过程中，AI 会按需自动调用已启用插件。</p>
              </el-alert>
            </el-card>

            <div class="tips-card">
              <h4>创作建议</h4>
              <ul>
                <li>填写的信息越详细，生成结果通常越稳定。</li>
                <li>补充说明里可以写额外要求、口吻和结构偏好。</li>
                <li>完成初稿后可继续优化，提高可读性和表达质量。</li>
              </ul>
            </div>
          </div>
        </el-col>

        <el-col :xs="24" :lg="14">
          <div class="preview-section">
            <div class="preview-header">
              <div>
                <h3>内容编辑</h3>
                <div class="preview-meta" v-if="currentCreation">
                  <el-tag size="small" effect="plain">字数：{{ contentStats.wordCount }}</el-tag>
                  <el-tag size="small" effect="plain">预计阅读：{{ contentStats.readingMinutes }} 分钟</el-tag>
                </div>
              </div>
              <div class="preview-actions">
                <el-button v-if="currentCreation" :icon="RefreshRight" @click="handleRegenerate" :loading="generating">重新生成</el-button>
                <el-button v-if="currentCreation" :icon="MagicStick" @click="showOptimizeDialog = true">优化</el-button>
                <el-button v-if="currentCreation" :icon="Download" @click="handleExport">导出</el-button>
              </div>
            </div>

            <!-- 封面图预览 -->
            <div v-if="coverImage" class="cover-image-preview">
              <img :src="coverImage.thumb_url || coverImage.url" :alt="coverImage.alt" />
              <div class="cover-actions">
                <el-button size="small" type="danger" text @click="coverImage = null">
                  <el-icon><Delete /></el-icon>
                  移除封面
                </el-button>
              </div>
            </div>

            <div v-if="!currentCreation" class="empty-preview">
              <el-empty description="请先填写信息并生成内容" />
            </div>
            <div v-else class="content-editor">
              <MdEditor
                v-model="markdownContent"
                :theme="editorTheme"
                :preview="true"
                :toolbars="toolbars"
                :footers="[]"
                @onChange="handleContentChange"
                style="height: 600px"
              />
            </div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <el-dialog v-model="showOptimizeDialog" title="内容优化" width="500px">
      <el-form label-position="top">
        <el-form-item label="优化类型">
          <el-checkbox-group v-model="optimizeTypes">
            <el-checkbox label="seo">SEO 优化</el-checkbox>
            <el-checkbox label="readability">可读性</el-checkbox>
            <el-checkbox label="style">文风调整</el-checkbox>
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

    <!-- 标题助手对话框 -->
    <el-dialog v-model="showTitleDialog" title="标题助手" width="800px" destroy-on-close>
      <el-tabs v-model="titleTabActive">
        <el-tab-pane label="优化标题" name="optimize">
          <TitleOptimizer
            ref="titleOptimizerRef"
            :initial-title="currentTitle"
            @select="handleTitleSelect"
          />
        </el-tab-pane>
        <el-tab-pane label="生成标题" name="generate">
          <TitleGenerator
            ref="titleGeneratorRef"
            @select="handleTitleSelect"
          />
        </el-tab-pane>
      </el-tabs>
    </el-dialog>

    <!-- 图片选择器 -->
    <ImagePicker
      ref="imagePickerRef"
      :content-for-suggest="markdownContent"
      @select="handleImageSelect"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Download, MagicStick, RefreshRight, Upload, EditPen, Picture, Delete } from '@element-plus/icons-vue'
import { MdEditor, type ToolbarNames } from 'md-editor-v3'
import 'md-editor-v3/lib/style.css'
import { generateContent, optimizeContent, regenerateContent } from '@/api/writing'
import { publishContent } from '@/api/publish'
import { getAIModels } from '@/api/models'
import { getCreation } from '@/api/creations'
import { analyzeContent, imitateContent } from '@/api/viralAnalyzer'
import PluginSelector from '@/components/PluginSelector.vue'
import DynamicToolForm from '@/components/writing/DynamicToolForm.vue'
import TitleOptimizer from '@/components/title/TitleOptimizer.vue'
import TitleGenerator from '@/components/title/TitleGenerator.vue'
import ImagePicker from '@/components/image/ImagePicker.vue'
import { getToolFormConfig } from '@/config/writingToolForms'
import type { AIModel, Creation } from '@/types'
import type { ImageItem } from '@/api/imageStock'

const router = useRouter()
const route = useRoute()
const toolType = computed(() => route.params.toolType as string)
const editId = computed(() => route.query.id as string | undefined)

// 热点标题填充的字段映射
const topicFieldMapping: Record<string, string> = {
  wechat_article: 'topic',
  xiaohongshu_note: 'topic',
  official_document: 'topic',
  news_article: 'topic',
  video_script: 'topic',
  academic_paper: 'title',
  story_novel: 'theme',
  viral_imitate: 'new_topic',
  business_plan: 'project_name',
  marketing_copy: 'product',
}

// 读取 query 参数（从热点跳转过来）
const queryTopic = route.query.topic as string | undefined
const queryDirection = route.query.direction as string | undefined

// 根据工具类型获取目标字段名
const getTopicFieldName = (tool: string): string | null => {
  return topicFieldMapping[tool] || null
}

// 初始化 formData（包含 query 参数）
const initFormDataFromQuery = (): Record<string, any> => {
  if (!queryTopic) return {}
  
  const fieldName = getTopicFieldName(route.params.toolType as string)
  if (!fieldName) return {}
  
  const data: Record<string, any> = {
    [fieldName]: queryTopic,
  }
  
  // 如果有创作方向，填充到 additional_description
  if (queryDirection) {
    data.additional_description = `创作方向：${queryDirection}`
  }
  
  return data
}

const toolInfo = computed(() => {
  const config = getToolFormConfig(toolType.value)
  if (config) {
    return { name: config.name, description: config.description }
  }
  return { name: 'AI 写作工具', description: '智能生成高质量写作内容。' }
})

const dynamicFormRef = ref<InstanceType<typeof DynamicToolForm>>()
const formData = ref<Record<string, any>>(initFormDataFromQuery())
const aiModels = ref<AIModel[]>([])
const selectedModel = ref<number>()
const markdownContent = ref('')
const editorTheme = ref<'light' | 'dark'>('light')
const toolbars: ToolbarNames[] = ['bold','underline','italic','strikeThrough','-','title','sub','sup','quote','unorderedList','orderedList','task','-','codeRow','code','link','image','table','-','revoke','next','=','preview','htmlPreview','catalog']
const currentCreation = ref<Creation>()
const generating = ref(false)
const optimizing = ref(false)
const publishing = ref(false)
const showOptimizeDialog = ref(false)
const showPublishDialog = ref(false)
const optimizeTypes = ref<string[]>([])
const selectedPlatforms = ref<string[]>([])
const selectedPlugins = ref<string[]>([])

// 标题助手相关
const showTitleDialog = ref(false)
const titleTabActive = ref('optimize')
const titleOptimizerRef = ref<InstanceType<typeof TitleOptimizer>>()
const titleGeneratorRef = ref<InstanceType<typeof TitleGenerator>>()

// 配图相关
const imagePickerRef = ref<InstanceType<typeof ImagePicker>>()
const coverImage = ref<ImageItem | null>(null)

// 获取当前标题
const currentTitle = computed(() => {
  return formData.value.title || currentCreation.value?.title || ''
})

const onPluginSelectionChange = (plugins: string[]) => {
  console.log('Selected plugins:', plugins)
}

const contentStats = computed(() => {
  const text = markdownContent.value.replace(/[#*`\[\]()_~>-]/g, '').trim()
  const wordCount = text.replace(/\s+/g, '').length
  const readingMinutes = Math.max(1, Math.ceil(wordCount / 300))
  return { wordCount, readingMinutes }
})

const handleContentChange = (value: string) => {
  console.log('Content changed, length:', value.length)
}

const handleGenerate = async () => {
  if (dynamicFormRef.value) {
    const valid = await dynamicFormRef.value.validate()
    if (!valid) {
      ElMessage.warning('请填写必填字段')
      return
    }
  }

  const params = dynamicFormRef.value?.getFormData() || {}
  generating.value = true
  try {
    let res: Creation
    
    // 爆款分析使用专用 API
    if (toolType.value === 'viral_analyze') {
      const analyzeRes = await analyzeContent({
        content: params.content,
        title: params.title || undefined,
        platform: params.platform || undefined,
      })
      // 将分析结果格式化为 Markdown
      const analysisContent = formatAnalysisResult(analyzeRes)
      res = {
        id: 0,
        user_id: 0,
        tool_type: 'viral_analyze',
        title: analyzeRes.title || '爆款分析报告',
        output_content: analysisContent,
        status: 'completed',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      } as Creation
    }
    // 爆款模仿使用专用 API
    else if (toolType.value === 'viral_imitate') {
      const imitateRes = await imitateContent({
        reference_content: params.reference_content,
        reference_title: params.reference_title || undefined,
        new_topic: params.new_topic,
        platform: params.platform || undefined,
        style_strength: params.style_strength || 80,
        keep_structure: params.keep_structure !== false,
        additional_requirements: params.additional_description || undefined,
      })
      // 将模仿结果转换为 Creation 格式
      res = {
        id: imitateRes.creation_id || 0,
        user_id: 0,
        tool_type: 'viral_imitate',
        title: imitateRes.title,
        output_content: imitateRes.content,
        status: 'completed',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      } as Creation
    } else {
      // 其他工具使用通用写作 API
      res = await generateContent({ tool_type: toolType.value, params, ai_model_id: selectedModel.value, enabled_plugins: selectedPlugins.value.length > 0 ? selectedPlugins.value : undefined })
    }
    
    currentCreation.value = res
    markdownContent.value = res.output_content || res.content || ''
    ElMessage.success('生成成功')
  } catch (error: any) {
    ElMessage.error(error.message || '生成失败')
  } finally {
    generating.value = false
  }
}

// 格式化爆款分析结果为 Markdown
const formatAnalysisResult = (result: any): string => {
  let md = `# 爆款分析报告\n\n`
  md += `## 基本信息\n\n`
  md += `- **文章标题**: ${result.title || '未知'}\n`
  md += `- **内容类别**: ${result.category || '未知'}\n`
  md += `- **爆款指数**: ${result.viral_score}/100\n`
  md += `- **语气风格**: ${result.tone || '未知'}\n`
  md += `- **目标受众**: ${result.target_audience || '未知'}\n\n`
  
  if (result.emotional_triggers && result.emotional_triggers.length > 0) {
    md += `## 情感触发点\n\n`
    result.emotional_triggers.forEach((trigger: string) => {
      md += `- ${trigger}\n`
    })
    md += `\n`
  }
  
  if (result.viral_elements && result.viral_elements.length > 0) {
    md += `## 爆款元素分析\n\n`
    result.viral_elements.forEach((elem: any) => {
      md += `### ${elem.name} (${elem.score}分)\n\n`
      md += `${elem.description}\n\n`
      if (elem.examples && elem.examples.length > 0) {
        md += `**示例:**\n`
        elem.examples.forEach((ex: string) => {
          md += `> ${ex}\n`
        })
        md += `\n`
      }
    })
  }
  
  if (result.structure) {
    md += `## 结构分析\n\n`
    md += `- **开头钩子**: ${result.structure.opening_hook || '未知'}\n`
    md += `- **结尾CTA**: ${result.structure.closing_cta || '未知'}\n`
    md += `- **过渡风格**: ${result.structure.transition_style || '未知'}\n\n`
  }
  
  if (result.writing_techniques && result.writing_techniques.length > 0) {
    md += `## 写作技巧\n\n`
    result.writing_techniques.forEach((tech: string) => {
      md += `- ${tech}\n`
    })
    md += `\n`
  }
  
  if (result.keywords && result.keywords.length > 0) {
    md += `## 核心关键词\n\n`
    md += result.keywords.map((kw: string) => `\`${kw}\``).join(' ')
    md += `\n\n`
  }
  
  if (result.improvement_suggestions && result.improvement_suggestions.length > 0) {
    md += `## 改进建议\n\n`
    result.improvement_suggestions.forEach((sug: string, idx: number) => {
      md += `${idx + 1}. ${sug}\n`
    })
  }
  
  return md
}

const handleRegenerate = async () => {
  if (!currentCreation.value) return
  generating.value = true
  try {
    const res = await regenerateContent(currentCreation.value.id)
    currentCreation.value = res
    markdownContent.value = res.output_content || res.content || ''
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
    const res = await optimizeContent(currentCreation.value.id, { optimize_types: optimizeTypes.value })
    currentCreation.value = res
    markdownContent.value = res.output_content || res.content || ''
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
    await publishContent({ creation_id: currentCreation.value.id, platforms: selectedPlatforms.value } as any)
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
  const blob = new Blob([markdownContent.value], { type: 'text/markdown' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${currentCreation.value.title || '内容'}.md`
  a.click()
  URL.revokeObjectURL(url)
}

// 标题选择处理
const handleTitleSelect = (title: string) => {
  // 更新表单中的标题
  if (formData.value) {
    formData.value.title = title
  }
  // 如果已有创作记录，也更新其标题
  if (currentCreation.value) {
    currentCreation.value.title = title
  }
  showTitleDialog.value = false
  ElMessage.success('已应用新标题')
}

// 打开图片选择器
const openImagePicker = () => {
  // 根据内容生成默认搜索词
  const defaultQuery = formData.value.topic || formData.value.title || ''
  imagePickerRef.value?.open(defaultQuery)
}

// 图片选择处理
const handleImageSelect = (image: ImageItem) => {
  coverImage.value = image
  ElMessage.success('已选择封面图')
}

const loadModels = async () => {
  try {
    const res = await getAIModels('text')
    aiModels.value = Array.isArray(res) ? res : (res.data || [])
    if (aiModels.value.length > 0) {
      selectedModel.value = aiModels.value[0].id
    }
  } catch (error: any) {
    ElMessage.error(error.message || '加载模型失败')
  }
}

const loadCreationForEdit = async (id: string) => {
  try {
    const res = await getCreation(parseInt(id))
    const creation = res.data || res
    currentCreation.value = creation
    markdownContent.value = creation.output_content || creation.content || ''
    const params = creation.input_params || creation.metadata || creation.input_data || {}
    formData.value = { ...params }
    ElMessage.success('已加载历史创作内容')
  } catch (error: any) {
    ElMessage.error(error.message || '加载创作记录失败')
  }
}

onMounted(async () => {
  await loadModels()
  if (editId.value) {
    await loadCreationForEdit(editId.value)
  }
})
</script>

<style scoped lang="scss">
.writing-editor {
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding: 28px;
  max-width: 1440px;
  margin: 0 auto;
}

.editor-hero {
  padding: 30px;
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 30px;
  background:
    radial-gradient(circle at top right, rgba(125, 211, 252, 0.38), transparent 28%),
    linear-gradient(135deg, rgba(239, 246, 255, 0.94), rgba(255, 255, 255, 0.92));
  box-shadow: 0 24px 60px rgba(15, 23, 42, 0.08);
}

.eyebrow {
  margin: 0 0 10px;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: #2563eb;
}

.editor-hero h1 {
  margin: 0 0 10px;
  font-size: clamp(30px, 4vw, 42px);
  color: #12304a;
}

.editor-hero p {
  margin: 0;
  max-width: 760px;
  font-size: 15px;
  line-height: 1.75;
  color: #60758e;
}

:deep(.el-card) {
  border-radius: 26px;
  border: 1px solid rgba(148, 163, 184, 0.2);
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 20px 44px rgba(15, 23, 42, 0.07);
}

.editor-card :deep(.el-card__header) {
  padding: 18px 24px;
}

.editor-card :deep(.el-card__body) {
  padding: 24px;
}

.card-header,
.header-left,
.plugin-header,
.preview-header,
.preview-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.header-left h2,
.input-section h3,
.preview-header h3 {
  margin: 0;
  color: #12304a;
}

.input-section,
.preview-section {
  height: 100%;
}

.generate-block {
  margin-top: 20px;
}

.generate-button {
  width: 100%;
}

.side-card {
  margin-top: 18px;
  border-radius: 22px;
  background: linear-gradient(180deg, rgba(248, 250, 252, 0.96), rgba(239, 246, 255, 0.82));
}

.plugin-selector-wrapper {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.plugin-hint {
  font-size: 13px;
  line-height: 1.6;
  color: #64748b;
}

.plugin-alert {
  margin-top: 12px;
}

.tips-card {
  margin-top: 18px;
  padding: 18px 20px;
  border: 1px solid rgba(148, 163, 184, 0.18);
  border-radius: 22px;
  background: linear-gradient(180deg, rgba(248, 250, 252, 0.96), rgba(239, 246, 255, 0.82));
}

.tips-card h4 {
  margin: 0 0 10px;
  color: #12304a;
}

.tips-card ul {
  margin: 0;
  padding-left: 18px;
  color: #60758e;
  line-height: 1.8;
}

.preview-header {
  align-items: flex-start;
  margin-bottom: 16px;
}

.preview-meta {
  display: flex;
  gap: 8px;
  margin-top: 10px;
}

.preview-section .preview-actions {
  justify-content: flex-end;
  flex-wrap: wrap;
}

.empty-preview {
  min-height: 520px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px dashed rgba(148, 163, 184, 0.32);
  border-radius: 22px;
  background: linear-gradient(180deg, rgba(248, 250, 252, 0.96), rgba(239, 246, 255, 0.7));
}

.cover-image-preview {
  position: relative;
  margin-bottom: 16px;
  border-radius: 16px;
  overflow: hidden;
  background: #f5f7fa;

  img {
    width: 100%;
    max-height: 240px;
    object-fit: cover;
    display: block;
  }

  .cover-actions {
    position: absolute;
    top: 12px;
    right: 12px;
    display: flex;
    gap: 8px;

    .el-button {
      background: rgba(255, 255, 255, 0.9);
      border-radius: 8px;
      backdrop-filter: blur(8px);
    }
  }
}

.content-editor {
  min-height: 520px;
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 22px;
  overflow: hidden;
}

.content-editor :deep(.md-editor) {
  --md-bk-color: #fff;
  min-height: 520px;
}

.content-editor :deep(.md-editor-toolbar) {
  padding: 10px 14px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.18);
  background: rgba(248, 250, 252, 0.92);
}

.content-editor :deep(.md-editor-input),
.content-editor :deep(.md-editor-preview) {
  padding: 18px;
  line-height: 1.8;
}

.content-editor :deep(blockquote) {
  margin: 16px 0;
  padding: 12px 16px;
  border-left: 4px solid #3b82f6;
  border-radius: 0 14px 14px 0;
  background: rgba(239, 246, 255, 0.9);
}

@media (max-width: 992px) {
  .writing-editor {
    padding: 16px;
  }

  .editor-card :deep(.el-card__body) {
    padding: 16px;
  }

  .preview-section {
    margin-top: 24px;
  }

  .content-editor,
  .empty-preview,
  .content-editor :deep(.md-editor) {
    min-height: 380px;
  }
}

@media (max-width: 576px) {
  .writing-editor {
    gap: 16px;
    padding: 12px;
  }

  .editor-hero,
  .editor-card :deep(.el-card__body) {
    padding: 16px;
  }

  .editor-card :deep(.el-card__header) {
    padding: 14px 16px;
  }

  .card-header,
  .header-left,
  .preview-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .preview-section .preview-actions {
    width: 100%;
    justify-content: flex-start;
  }
}
</style>
