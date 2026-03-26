<template>
  <div class="ppt-generation">
    <!-- 左侧：输入表单 -->
    <div class="left-panel">
      <el-card class="form-card">
        <template #header>
          <div class="card-header">
            <span>PPT 生成</span>
            <el-tag type="info" size="small">消耗10积分</el-tag>
          </div>
        </template>

        <el-form :model="form" label-position="top">
          <el-form-item label="选择模型" required>
            <el-select v-model="form.model_id" placeholder="请选择文本生成模型" style="width: 100%">
              <el-option
                v-for="model in textModels"
                :key="model.id"
                :label="`${model.name}`"
                :value="model.id"
              />
            </el-select>
            <div v-if="!textModels.length" class="model-hint">
              暂无可用的文本生成模型，请先在 <router-link to="/settings">设置</router-link> 中添加
            </div>
          </el-form-item>
          
          <el-form-item label="主题" required>
            <el-input 
              v-model="form.topic" 
              placeholder="输入PPT主题，如：人工智能的发展与未来" 
              :rows="2"
              type="textarea"
            />
          </el-form-item>
          
          <el-row :gutter="12">
            <el-col :span="12">
              <el-form-item label="页数">
                <el-input-number v-model="form.slides_count" :min="5" :max="30" style="width: 100%" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="风格">
                <el-select v-model="form.style" style="width: 100%">
                  <el-option label="商务" value="business" />
                  <el-option label="现代" value="modern" />
                  <el-option label="简约" value="minimal" />
                  <el-option label="创意" value="creative" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-form-item>
            <el-button 
              type="primary" 
              :loading="generatingOutline" 
              @click="handleGenerateOutline"
              style="width: 100%"
              size="large"
            >
              <el-icon><MagicStick /></el-icon>
              生成大纲
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>
      
      <!-- 历史记录 -->
      <el-card class="history-card">
        <template #header>
          <div class="card-header">
            <span>历史记录</span>
          </div>
        </template>
        
        <el-tabs v-model="historyTab" class="history-tabs">
          <el-tab-pane label="大纲" name="outline">
            <div v-if="loadingHistory" class="loading-state">
              <el-skeleton :rows="3" animated />
            </div>
            <el-empty v-else-if="historyList.length === 0" description="暂无大纲记录" :image-size="60" />
            <div v-else class="history-list">
              <div 
                v-for="item in historyList" 
                :key="item.id" 
                class="history-item"
                @click="loadHistoryItem(item.id)"
              >
                <div class="history-title">{{ item.topic }}</div>
                <div class="history-meta">
                  <span>{{ item.slides_count }}页</span>
                  <span>{{ formatTime(item.created_at) }}</span>
                </div>
              </div>
            </div>
          </el-tab-pane>
          
          <el-tab-pane label="已保存PPT" name="saved">
            <div v-if="loadingSaved" class="loading-state">
              <el-skeleton :rows="3" animated />
            </div>
            <el-empty v-else-if="savedPPTs.length === 0" description="暂无已保存PPT" :image-size="60" />
            <div v-else class="history-list">
              <div 
                v-for="item in savedPPTs" 
                :key="item.id" 
                class="history-item"
                @click="openSavedPPT(item.id)"
              >
                <div class="history-title">{{ item.title }}</div>
                <div class="history-meta">
                  <span>{{ formatTime(item.created_at) }}</span>
                </div>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </el-card>
    </div>

    <!-- 右侧：内容区域 -->
    <div class="right-panel">
      <!-- 步骤指示器 -->
      <div class="step-indicator" v-if="outline">
        <div 
          class="step-item" 
          :class="{ active: currentStep === 'edit', completed: currentStep !== 'edit' && outline }"
          @click="currentStep = 'edit'"
        >
          <span class="step-num">1</span>
          <span class="step-text">编辑大纲</span>
        </div>
        <div class="step-line"></div>
        <div 
          class="step-item" 
          :class="{ active: currentStep === 'template' }"
          @click="outline && (currentStep = 'template')"
        >
          <span class="step-num">2</span>
          <span class="step-text">选择模板</span>
        </div>
      </div>

      <el-card class="content-card">
        <!-- 未生成大纲时的提示 -->
        <el-empty v-if="!outline" description="请在左侧输入主题并点击生成大纲" :image-size="120" />
        
        <!-- 步骤1: 编辑大纲 -->
        <div v-else-if="currentStep === 'edit'" class="outline-edit-section">
          <div class="section-header">
            <h3>编辑大纲</h3>
            <p class="tip">点击内容可直接编辑，编辑完成后点击"下一步"选择模板</p>
          </div>
          
          <div class="outline-edit">
            <el-input 
              v-model="editableOutline.title" 
              placeholder="PPT标题"
              size="large"
              class="title-input"
            />
            <el-input 
              v-model="editableOutline.subtitle" 
              placeholder="副标题（可选）"
              class="subtitle-input"
            />
            
            <div class="slides-edit">
              <div v-for="(slide, index) in editableOutline.slides" :key="index" class="slide-edit-item">
                <div class="slide-edit-header">
                  <span class="slide-num">{{ index + 1 }}</span>
                  <el-select v-model="slide.slide_type" size="small" style="width: 100px">
                    <el-option label="封面" value="title" />
                    <el-option label="内容" value="content" />
                    <el-option label="章节" value="section" />
                    <el-option label="结尾" value="ending" />
                  </el-select>
                  <el-input 
                    v-model="slide.title" 
                    placeholder="页面标题"
                    size="small"
                    class="slide-title-input"
                  />
                  <el-button link type="danger" size="small" @click="removeSlide(index)">
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </div>
                <div v-if="slide.slide_type === 'content'" class="bullets-edit">
                  <div v-for="(_, bIndex) in slide.bullets" :key="bIndex" class="bullet-item">
                    <span class="bullet-dot">{{ bIndex + 1 }}</span>
                    <el-input v-model="slide.bullets![bIndex]" placeholder="要点" size="small" />
                    <el-button link type="danger" size="small" @click="removeBullet(index, bIndex)">
                      <el-icon><Close /></el-icon>
                    </el-button>
                  </div>
                  <el-button link type="primary" size="small" @click="addBullet(index)">
                    + 添加要点
                  </el-button>
                </div>
              </div>
            </div>
            
            <el-button link type="primary" @click="addSlide" style="margin-top: 8px">
              + 添加页面
            </el-button>
          </div>
          
          <div class="section-footer">
            <el-button @click="outline = null">返回</el-button>
            <el-button type="primary" @click="currentStep = 'template'">
              下一步：选择模板
              <el-icon><ArrowRight /></el-icon>
            </el-button>
          </div>
        </div>
        
        <!-- 步骤2: 选择模板 -->
        <div v-else-if="currentStep === 'template'" class="template-section">
          <div class="section-header">
            <h3>选择模板</h3>
            <p class="tip">选择一个PPT模板，系统会根据模板样式生成PPT</p>
            <el-button type="primary" link @click="showUploadDialog = true">
              <el-icon><Upload /></el-icon>
              上传PPTX模板
            </el-button>
          </div>
          
          <div class="template-grid">
            <!-- 用户上传的模板 -->
            <div 
              v-for="template in userTemplates" 
              :key="'user-' + template.id" 
              class="template-card"
              :class="{ active: selectedTemplateId === 'user-' + template.id }"
              @click="selectedTemplateId = 'user-' + template.id"
            >
              <div class="template-cover">
                <img v-if="template.thumbnail" :src="template.thumbnail" :alt="template.name" />
                <div v-else class="template-placeholder">{{ template.name.charAt(0) }}</div>
                <div v-if="selectedTemplateId === 'user-' + template.id" class="selected-badge">
                  <el-icon><Check /></el-icon>
                </div>
                <el-button 
                  v-if="isPPTTemplateOwner(template)"
                  class="delete-btn"
                  type="danger"
                  size="small"
                  circle
                  @click.stop="handleDeleteTemplate(template)"
                >
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
              <div class="template-info">
                <div class="template-name">{{ template.name }}</div>
                <div class="template-desc">{{ template.is_system ? '系统模板' : '自定义模板' }}</div>
              </div>
            </div>
            
            <!-- 系统预设模板 -->
            <div 
              v-for="template in pptTemplates" 
              :key="template.id" 
              class="template-card"
              :class="{ active: selectedTemplateId === template.id }"
              @click="selectedTemplateId = template.id"
            >
              <div class="template-cover">
                <img :src="template.cover" :alt="template.name" />
                <div v-if="selectedTemplateId === template.id" class="selected-badge">
                  <el-icon><Check /></el-icon>
                </div>
              </div>
              <div class="template-info">
                <div class="template-name">{{ template.name }}</div>
                <div class="template-desc">{{ template.style }}</div>
              </div>
            </div>
          </div>
          
          <div class="section-footer">
            <el-button @click="currentStep = 'edit'">
              <el-icon><ArrowLeft /></el-icon>
              返回编辑大纲
            </el-button>
            <el-button 
              type="primary" 
              :loading="generatingPPT"
              @click="handleGeneratePPT"
              :disabled="!selectedTemplateId"
            >
              <el-icon><VideoPlay /></el-icon>
              生成PPT
            </el-button>
          </div>
        </div>
      </el-card>
    </div>
    
    <!-- 上传模板对话框 -->
    <el-dialog v-model="showUploadDialog" title="上传PPTX模板" width="700px">
      <PPTXUpload @success="handleUploadSuccess" @cancel="showUploadDialog = false" />
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { MagicStick, Delete, Close, ArrowLeft, ArrowRight, VideoPlay, Check, Upload } from '@element-plus/icons-vue'
import request from '@/api/request'
import { getAIModels } from '@/api/models'
import { generatePPTOutline, getPPTOutlines, getPPTOutline, getSavedPPTs, getSavedPPT, type PPTOutline, type PPTOutlineItem } from '@/api/ppt'
import { getPPTTemplates, getPPTTemplateDetail, deletePPTTemplate, type PPTTemplate } from '@/api/pptTemplate'
import { convertOutlineToAIPPT } from '@/utils/pptistConverter'
import PPTXUpload from '@/components/ppt/PPTXUpload.vue'
import { useUserStore } from '@/store/user'
import type { AIModel } from '@/types'

const router = useRouter()
const userStore = useUserStore()
const generatingOutline = ref(false)
const generatingPPT = ref(false)
const loadingHistory = ref(false)
const loadingSaved = ref(false)
const loadingTip = ref('加载中...')
const textModels = ref<AIModel[]>([])
const outline = ref<PPTOutline | null>(null)
const editableOutline = ref<PPTOutline>({ title: '', slides: [] })
const historyList = ref<PPTOutlineItem[]>([])
const savedPPTs = ref<{ id: number; title: string; created_at: string }[]>([])
const userTemplates = ref<PPTTemplate[]>([])
const selectedTemplateId = ref<string>('template_1')
const currentStep = ref<'edit' | 'template'>('edit')
const historyTab = ref('outline')
const showUploadDialog = ref(false)

// PPTist内置模板（带封面图）
const pptTemplates = ref([
  { id: 'template_1', name: '简约红', style: '简约', description: '简洁大方的红色主题', cover: '/pptist/public/imgs/template_1.webp' },
  { id: 'template_2', name: '商务蓝', style: '商务', description: '专业商务蓝色主题', cover: '/pptist/public/imgs/template_2.webp' },
  { id: 'template_3', name: '清新绿', style: '清新', description: '清新自然的绿色主题', cover: '/pptist/public/imgs/template_3.webp' },
  { id: 'template_4', name: '典雅紫', style: '典雅', description: '高端典雅紫色主题', cover: '/pptist/public/imgs/template_4.webp' },
  { id: 'template_5', name: '活力橙', style: '活力', description: '充满活力的橙色主题', cover: '/pptist/public/imgs/template_5.webp' },
  { id: 'template_6', name: '科技黑', style: '科技', description: '科技感黑色主题', cover: '/pptist/public/imgs/template_6.webp' },
  { id: 'template_7', name: '温暖黄', style: '温暖', description: '温馨舒适的黄色主题', cover: '/pptist/public/imgs/template_7.webp' },
  { id: 'template_8', name: '优雅粉', style: '优雅', description: '优雅浪漫的粉色主题', cover: '/pptist/public/imgs/template_8.webp' },
])

const form = reactive({
  model_id: undefined as number | undefined,
  topic: '',
  slides_count: 10,
  style: 'business',
  language: 'zh-CN',
})

const formatTime = (timeStr: string) => {
  const date = new Date(timeStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  if (diff < 604800000) return `${Math.floor(diff / 86400000)}天前`
  
  return date.toLocaleDateString()
}

const loadTextModels = async () => {
  try {
    const res = await getAIModels('text')
    textModels.value = Array.isArray(res) ? res : (res as any).data || []
    if (textModels.value.length && !form.model_id) {
      form.model_id = textModels.value[0].id
    }
  } catch {
    ElMessage.error('加载文本模型失败')
  }
}

const loadHistory = async () => {
  loadingHistory.value = true
  try {
    const res = await getPPTOutlines(0, 20)
    historyList.value = res.data?.items || []
  } catch (e) {
    console.error('加载历史记录失败:', e)
  } finally {
    loadingHistory.value = false
  }
}

const loadHistoryItem = async (id: number) => {
  try {
    const res = await getPPTOutline(id)
    outline.value = res.data
    editableOutline.value = JSON.parse(JSON.stringify(res.data))
    currentStep.value = 'edit'
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '加载失败')
  }
}

const loadSavedPPTs = async () => {
  loadingSaved.value = true
  try {
    const res = await getSavedPPTs(0, 20)
    savedPPTs.value = res.data?.items || []
  } catch (e) {
    console.error('加载已保存PPT失败:', e)
  } finally {
    loadingSaved.value = false
  }
}

const loadUserTemplates = async () => {
  try {
    const res = await getPPTTemplates(0, 20)
    userTemplates.value = res.data?.items || []
  } catch (e) {
    console.error('加载用户模板失败:', e)
  }
}

const handleUploadSuccess = (template: { id: number; name: string; thumbnail?: string }) => {
  showUploadDialog.value = false
  userTemplates.value.unshift({
    id: template.id,
    name: template.name,
    thumbnail: template.thumbnail,
    is_system: false,
    use_count: 0,
    created_at: new Date().toISOString(),
  })
  selectedTemplateId.value = 'user-' + template.id
  ElMessage.success('模板上传成功')
}

const handleDeleteTemplate = async (template: PPTTemplate) => {
  // 权限检查
  if (!isPPTTemplateOwner(template)) {
    ElMessage.warning('只能删除自己创建的模板')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确定要删除模板"${template.name}"吗？删除后无法恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    await deletePPTTemplate(template.id)
    
    // 从列表中移除
    const index = userTemplates.value.findIndex(t => t.id === template.id)
    if (index > -1) {
      userTemplates.value.splice(index, 1)
    }
    
    // 如果当前选中的是被删除的模板，重置选择
    if (selectedTemplateId.value === 'user-' + template.id) {
      selectedTemplateId.value = 'template_1'
    }
    
    ElMessage.success('模板删除成功')
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除模板失败:', error)
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
}

// 判断PPT模板是否属于当前用户
const isPPTTemplateOwner = (template: PPTTemplate): boolean => {
  // 系统模板不属于任何人
  if (template.is_system) return false
  // 如果没有user_id，认为是公共模板
  if (!template.user_id) return false
  // 判断是否是当前用户的模板
  const currentUserId = userStore.userInfo?.id
  return currentUserId !== undefined && template.user_id === currentUserId
}

const openSavedPPT = async (id: number) => {
  try {
    const res = await getSavedPPT(id)
    const pptData = res.data
    
    // 将slides保存到localStorage
    localStorage.setItem('pptist_slides', JSON.stringify(pptData.slides))
    if (pptData.template_id) {
      localStorage.setItem('pptist_template_id', pptData.template_id)
    }
    
    // 跳转到编辑器
    router.push('/ppt/editor')
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '加载失败')
  }
}

const handleGenerateOutline = async () => {
  if (!form.model_id) {
    ElMessage.warning('请选择模型')
    return
  }
  if (!form.topic.trim()) {
    ElMessage.warning('请输入主题')
    return
  }

  generatingOutline.value = true
  try {
    const res = await generatePPTOutline({
      model_id: form.model_id,
      topic: form.topic,
      slides_count: form.slides_count,
      style: form.style,
      language: form.language,
    })
    outline.value = res.data
    editableOutline.value = JSON.parse(JSON.stringify(res.data))
    currentStep.value = 'edit'
    ElMessage.success('大纲生成成功')
    
    loadHistory()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '生成失败')
  } finally {
    generatingOutline.value = false
  }
}

const handleGeneratePPT = async () => {
  if (!selectedTemplateId.value) {
    ElMessage.warning('请选择模板')
    return
  }
  if (!form.model_id) {
    ElMessage.warning('请选择AI模型')
    return
  }

  generatingPPT.value = true
  loadingTip.value = '正在用AI丰富内容...'
  
  try {
    // 1. 调用AI丰富大纲内容
    const enrichedOutline = await enrichOutlineWithAI(editableOutline.value)
    
    // 2. 将丰富后的大纲转换为AIPPT格式
    const aiSlides = convertOutlineToAIPPT(enrichedOutline)
    
    // 3. 准备存储数据
    const aipptData: any = {
      slides: aiSlides,
      templateId: selectedTemplateId.value
    }
    
    // 如果是用户上传的模板（user-前缀），预先加载模板数据
    if (selectedTemplateId.value.startsWith('user-')) {
      const templateIdNum = parseInt(selectedTemplateId.value.replace('user-', ''))
      try {
        const templateRes = await getPPTTemplateDetail(templateIdNum)
        console.log('获取到的模板数据:', templateRes.data)
        
        // 检查ppt_layout是否存在且包含slides
        const pptLayout = templateRes.data?.ppt_layout
        if (pptLayout && pptLayout.slides && Array.isArray(pptLayout.slides)) {
          aipptData.templateData = pptLayout
        } else {
          console.warn('模板数据格式不正确，将使用默认模板', pptLayout)
        }
      } catch (err) {
        console.error('获取模板详情失败:', err)
      }
    }
    
    // 4. 存储数据到localStorage
    localStorage.setItem('pptist_aippt_data', JSON.stringify(aipptData))
    
    ElMessage.success('内容已丰富，正在跳转到编辑器...')
    
    // 5. 跳转到编辑器
    router.push('/ppt/editor')
  } catch (e: any) {
    ElMessage.error(e.message || '生成失败')
    generatingPPT.value = false
  }
}

// 使用AI丰富大纲内容
const enrichOutlineWithAI = async (outline: PPTOutline): Promise<PPTOutline> => {
  const enrichedSlides = []
  
  for (const slide of outline.slides) {
    if (slide.slide_type === 'content' && slide.bullets && slide.bullets.length > 0) {
      try {
        // 调用AI为每个要点生成标题和详细内容
        const response = await request.post('/v1/ppt/enrich-slide', {
          model_id: form.model_id,
          title: slide.title,
          bullets: slide.bullets,
          style: form.style,
        })
        
        const items = response.data?.items || []
        
        // 如果AI生成了items，使用items中的text作为新的bullets
        if (items.length > 0) {
          enrichedSlides.push({
            ...slide,
            bullets: items.map((item: any) => item.text || item.title),
            // 可以在这里保存items用于后续更精细的处理
            enrichedItems: items,
          })
        } else {
          enrichedSlides.push(slide)
        }
      } catch {
        // 如果AI丰富失败，使用原始内容
        enrichedSlides.push(slide)
      }
    } else {
      enrichedSlides.push(slide)
    }
  }
  
  return {
    ...outline,
    slides: enrichedSlides,
  }
}

// 大纲编辑相关方法
const addSlide = () => {
  editableOutline.value.slides.push({
    slide_type: 'content',
    title: '',
    bullets: ['要点1', '要点2', '要点3'],
  })
}

const removeSlide = (index: number) => {
  editableOutline.value.slides.splice(index, 1)
}

const addBullet = (slideIndex: number) => {
  if (!editableOutline.value.slides[slideIndex].bullets) {
    editableOutline.value.slides[slideIndex].bullets = []
  }
  editableOutline.value.slides[slideIndex].bullets!.push('')
}

const removeBullet = (slideIndex: number, bulletIndex: number) => {
  editableOutline.value.slides[slideIndex].bullets!.splice(bulletIndex, 1)
}

// 同步编辑的大纲到预览
watch(editableOutline, (newVal) => {
  outline.value = JSON.parse(JSON.stringify(newVal))
}, { deep: true })

onMounted(() => {
  loadTextModels()
  loadHistory()
  loadSavedPPTs()
  loadUserTemplates()
})
</script>

<style scoped lang="scss">
.ppt-generation {
  display: flex;
  gap: 16px;
  height: 100%;
  padding: 16px;
  background: #f5f7fa;
}

.left-panel {
  width: 360px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.right-panel {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.form-card, .history-card, .content-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}

.history-card {
  flex: 1;
  min-height: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  
  :deep(.el-card__body) {
    flex: 1;
    overflow-y: auto;
    min-height: 0;
  }
}

.content-card {
  flex: 1;
  min-height: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  
  :deep(.el-card__body) {
    flex: 1;
    overflow-y: auto;
    min-height: 0;
    padding: 20px;
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.model-hint {
  margin-top: 8px;
  color: #909399;
  font-size: 12px;
  
  a {
    color: var(--el-color-primary);
  }
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.history-item {
  padding: 12px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  
  &:hover {
    background: #f5f7fa;
    border-color: #c0c4cc;
  }
}

.history-title {
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.history-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: #909399;
}

.loading-state {
  padding: 20px;
}

// 步骤指示器
.step-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}

.step-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.2s;
  color: #909399;
  
  &.active {
    background: var(--el-color-primary);
    color: #fff;
  }
  
  &.completed {
    color: var(--el-color-primary);
  }
}

.step-num {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  background: currentColor;
  color: #fff;
  
  .active & {
    background: #fff;
    color: var(--el-color-primary);
  }
}

.step-text {
  font-size: 14px;
}

.step-line {
  width: 40px;
  height: 2px;
  background: #e4e7ed;
}

// 编辑大纲部分
.outline-edit-section, .template-section {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.section-header {
  margin-bottom: 20px;
  
  h3 {
    margin: 0 0 8px 0;
    font-size: 18px;
    color: #303133;
  }
  
  .tip {
    margin: 0;
    font-size: 13px;
    color: #909399;
  }
}

.outline-edit {
  flex: 1;
  overflow-y: auto;
  padding-right: 8px;
}

.title-input {
  margin-bottom: 12px;
  
  :deep(.el-input__inner) {
    font-size: 18px;
    font-weight: 600;
  }
}

.subtitle-input {
  margin-bottom: 20px;
}

.slides-edit {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.slide-edit-item {
  padding: 16px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  background: #fafafa;
}

.slide-edit-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.slide-num {
  width: 28px;
  height: 28px;
  background: var(--el-color-primary);
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 500;
  flex-shrink: 0;
}

.slide-title-input {
  flex: 1;
}

.bullets-edit {
  padding-left: 36px;
}

.bullet-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.bullet-dot {
  width: 20px;
  height: 20px;
  background: #e4e7ed;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  color: #606266;
  flex-shrink: 0;
}

.section-footer {
  display: flex;
  justify-content: space-between;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #e4e7ed;
}

// 模板选择部分
.template-grid {
  flex: 1;
  overflow-y: auto;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  padding-right: 8px;
}

.template-card {
  border: 2px solid #e4e7ed;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s;
  
  &:hover {
    border-color: #c0c4cc;
    transform: translateY(-2px);
  }
  
  &.active {
    border-color: var(--el-color-primary);
    box-shadow: 0 4px 12px rgba(64, 158, 255, 0.2);
  }
}

.template-cover {
  position: relative;
  height: 120px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  
  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
}

.template-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  font-weight: bold;
  color: rgba(255, 255, 255, 0.8);
}

.selected-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 28px;
  height: 28px;
  background: var(--el-color-primary);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 16px;
}

.delete-btn {
  position: absolute;
  bottom: 8px;
  right: 8px;
  opacity: 0;
  transition: opacity 0.2s;
}

.template-card:hover .delete-btn {
  opacity: 1;
}

.template-info {
  padding: 12px;
}

.template-name {
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.template-desc {
  font-size: 12px;
  color: #909399;
}

@media (max-width: 1200px) {
  .template-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 900px) {
  .ppt-generation {
    flex-direction: column;
  }
  
  .left-panel {
    width: 100%;
  }
  
  .template-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
