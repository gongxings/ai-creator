<template>
  <div class="image-generation">
    <!-- 主体区域：左右结构 -->
    <div class="main-content">
      <!-- 左侧：参数面板 -->
      <div class="left-panel">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>AI 图片生成</span>
              <el-button type="primary" :loading="generating" @click="handleGenerate">
                <el-icon><VideoPlay /></el-icon>
                生成
              </el-button>
            </div>
          </template>

          <el-form :model="form" label-position="top">
            <el-form-item label="选择模型" required>
              <el-select v-model="form.model_id" placeholder="请选择图片生成模型" style="width: 100%">
                <el-option
                  v-for="model in imageModels"
                  :key="model.id"
                  :label="model.name"
                  :value="model.id"
                />
              </el-select>
              <div v-if="!imageModels.length" class="model-hint">
                暂无可用的图片生成模型，请先在 <router-link to="/settings">设置</router-link> 中添加支持图片生成的模型
              </div>
            </el-form-item>

            <el-form-item label="提示词" required>
              <el-input 
                v-model="form.prompt" 
                type="textarea" 
                :rows="6" 
                maxlength="2000" 
                show-word-limit
                placeholder="请描述你想生成的图片，例如：一只可爱的橘猫坐在窗台上看夕阳"
              />
            </el-form-item>

            <el-row :gutter="12">
              <el-col :span="12">
                <el-form-item label="宽度">
                  <el-select v-model="form.width" style="width: 100%">
                    <el-option :value="512" label="512" />
                    <el-option :value="768" label="768" />
                    <el-option :value="1024" label="1024" />
                    <el-option :value="1280" label="1280" />
                    <el-option :value="1536" label="1536" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="高度">
                  <el-select v-model="form.height" style="width: 100%">
                    <el-option :value="512" label="512" />
                    <el-option :value="768" label="768" />
                    <el-option :value="1024" label="1024" />
                    <el-option :value="1280" label="1280" />
                    <el-option :value="1536" label="1536" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item label="生成数量">
              <el-slider v-model="form.num_images" :min="1" :max="4" :step="1" show-stops />
            </el-form-item>
          </el-form>
        </el-card>
      </div>

      <!-- 右侧：预览区域 -->
      <div class="right-panel">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>生成结果</span>
              <el-button v-if="images.length" type="primary" link @click="downloadAll">
                <el-icon><Download /></el-icon>
                下载全部
              </el-button>
            </div>
          </template>

          <!-- Loading 状态 -->
          <div v-if="generating" class="loading-container">
            <div class="loading-animation">
              <div class="loading-spinner"></div>
            </div>
            <p class="loading-text">图片生成中...</p>
            <p class="loading-hint">AI 正在绘制你的创意，请稍候</p>
          </div>

          <!-- 图片预览 -->
          <div v-else-if="images.length" class="preview-grid">
            <div 
              v-for="(img, index) in images" 
              :key="index" 
              class="preview-item"
              @click="previewImage(img)"
            >
              <img :src="img" />
              <div class="preview-overlay">
                <el-button type="primary" circle size="small" @click.stop="downloadImage(img, index)">
                  <el-icon><Download /></el-icon>
                </el-button>
              </div>
            </div>
          </div>

          <!-- 空状态 -->
          <el-empty v-else description="请输入提示词，点击生成按钮开始创作" />
        </el-card>
      </div>
    </div>

    <!-- 底部：图库 -->
    <div class="gallery-section">
      <div class="gallery-header" @click="toggleGallery">
        <span>
          <el-icon><Picture /></el-icon>
          我的图库
          <el-tag size="small" type="info">{{ galleryImages.length }}</el-tag>
        </span>
        <el-icon :class="{ 'is-expanded': galleryExpanded }">
          <ArrowDown />
        </el-icon>
      </div>
      
      <el-collapse-transition>
        <div v-show="galleryExpanded" class="gallery-content">
          <div v-if="galleryLoading" class="gallery-loading">
            <el-icon class="is-loading"><Loading /></el-icon>
            <span>加载中...</span>
          </div>
          
          <div v-else-if="galleryImages.length" class="gallery-grid">
            <div 
              v-for="item in galleryImages" 
              :key="item.id" 
              class="gallery-item"
              @click="previewImage(item.url)"
            >
              <img :src="item.url" />
              <div class="gallery-overlay">
                <span class="gallery-date">{{ formatDate(item.created_at) }}</span>
              </div>
            </div>
          </div>
          
          <el-empty v-else description="暂无图片" :image-size="60" />
          
          <div v-if="galleryImages.length" class="gallery-pagination">
            <el-pagination
              v-model:current-page="galleryPage"
              :page-size="galleryPageSize"
              :total="galleryTotal"
              layout="prev, pager, next"
              small
              @current-change="loadGallery"
            />
          </div>
        </div>
      </el-collapse-transition>
    </div>

    <!-- 图片预览对话框 -->
    <el-dialog v-model="previewVisible" width="80%" :show-close="true" center>
      <img :src="previewUrl" style="width: 100%" />
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Loading, VideoPlay, Download, Picture, ArrowDown } from '@element-plus/icons-vue'
import request from '@/api/request'
import { getAIModels } from '@/api/models'
import type { AIModel } from '@/types'

interface GalleryItem {
  id: number
  url: string
  prompt: string
  created_at: string
}

const generating = ref(false)
const taskId = ref('')
const images = ref<string[]>([])
const imageModels = ref<AIModel[]>([])
let pollTimer: ReturnType<typeof setInterval> | null = null

// 图库相关
const galleryExpanded = ref(true)
const galleryLoading = ref(false)
const galleryImages = ref<GalleryItem[]>([])
const galleryPage = ref(1)
const galleryPageSize = 12
const galleryTotal = ref(0)

// 预览相关
const previewVisible = ref(false)
const previewUrl = ref('')

const form = reactive({
  model_id: undefined as number | undefined,
  prompt: '',
  width: 1024,
  height: 1024,
  num_images: 1,
})

const loadImageModels = async () => {
  try {
    const res = await getAIModels('image')
    imageModels.value = Array.isArray(res) ? res : (res as any).data || []
    if (imageModels.value.length && !form.model_id) {
      form.model_id = imageModels.value[0].id
    }
  } catch {
    ElMessage.error('加载图片模型失败')
  }
}

const stopPolling = () => {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

const pollTaskStatus = async (taskIdValue: string) => {
  try {
    const res = await request.get(`/v1/image/task/${taskIdValue}`)
    const status = res.data.status
    const taskImages = res.data.images || []
    
    if (status === 'completed' && taskImages.length > 0) {
      images.value = taskImages
      generating.value = false
      stopPolling()
      ElMessage.success('图片生成完成')
      loadGallery()
    } else if (status === 'failed') {
      generating.value = false
      stopPolling()
      ElMessage.error(res.data.error_message || '图片生成失败')
    }
  } catch (e: any) {
    generating.value = false
    stopPolling()
    ElMessage.error(e.response?.data?.detail || '获取任务状态失败')
  }
}

const handleGenerate = async () => {
  if (!form.model_id) {
    ElMessage.warning('请选择模型')
    return
  }
  if (!form.prompt.trim()) {
    ElMessage.warning('请输入提示词')
    return
  }

  generating.value = true
  images.value = []
  taskId.value = ''
  stopPolling()

  try {
    const res = await request.post('/v1/image/generate', {
      model_id: form.model_id,
      prompt: form.prompt,
      width: form.width,
      height: form.height,
      num_images: form.num_images,
    })
    taskId.value = res.data.task_id
    
    if (res.data.status === 'completed' && res.data.images?.length) {
      images.value = res.data.images
      generating.value = false
      ElMessage.success('图片生成完成')
      loadGallery()
    } else {
      pollTimer = setInterval(() => {
        pollTaskStatus(taskId.value)
      }, 2000)
    }
  } catch (e: any) {
    generating.value = false
    ElMessage.error(e.response?.data?.detail || '生成失败')
  }
}

// 图库相关
const toggleGallery = () => {
  galleryExpanded.value = !galleryExpanded.value
  if (galleryExpanded.value && !galleryImages.value.length) {
    loadGallery()
  }
}

const loadGallery = async () => {
  galleryLoading.value = true
  try {
    const res = await request.get('/v1/image/gallery', {
      params: {
        page: galleryPage.value,
        page_size: galleryPageSize,
      }
    })
    galleryImages.value = res.data.items || []
    galleryTotal.value = res.data.total || 0
  } catch (e: any) {
    ElMessage.error('加载图库失败')
  } finally {
    galleryLoading.value = false
  }
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}/${date.getDate()}`
}

// 预览和下载
const previewImage = (url: string) => {
  previewUrl.value = url
  previewVisible.value = true
}

const downloadImage = async (url: string, index: number) => {
  try {
    const response = await fetch(url)
    const blob = await response.blob()
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = `image_${index + 1}.png`
    link.click()
    URL.revokeObjectURL(link.href)
  } catch {
    window.open(url, '_blank')
  }
}

const downloadAll = () => {
  images.value.forEach((img, index) => {
    setTimeout(() => downloadImage(img, index), index * 500)
  })
}

onMounted(() => {
  loadImageModels()
  loadGallery()
})

onUnmounted(() => {
  stopPolling()
})
</script>

<style scoped>
.image-generation {
  padding: 20px;
  min-height: 100vh;
  background: #f5f7fa;
}

.main-content {
  display: flex;
  gap: 20px;
  min-height: 500px;
}

.left-panel {
  width: 380px;
  flex-shrink: 0;
}

.left-panel :deep(.el-card) {
  height: 100%;
}

.left-panel :deep(.el-card__body) {
  overflow-y: auto;
  max-height: calc(100% - 60px);
}

.right-panel {
  flex: 1;
  min-width: 0;
}

.right-panel :deep(.el-card) {
  height: 100%;
}

.right-panel :deep(.el-card__body) {
  height: calc(100% - 60px);
  display: flex;
  flex-direction: column;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.model-hint {
  margin-top: 8px;
  color: #909399;
  font-size: 12px;
}

.model-hint a {
  color: var(--el-color-primary);
}

/* Loading 动画 */
.loading-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.loading-animation {
  width: 80px;
  height: 80px;
  position: relative;
}

.loading-spinner {
  width: 100%;
  height: 100%;
  border: 4px solid #e5e7eb;
  border-top-color: var(--el-color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  margin-top: 20px;
  font-size: 16px;
  color: #303133;
  font-weight: 500;
}

.loading-hint {
  margin-top: 8px;
  font-size: 13px;
  color: #909399;
}

/* 预览网格 */
.preview-grid {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
  overflow-y: auto;
  padding: 4px;
}

.preview-item {
  position: relative;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  aspect-ratio: 1;
  background: #f5f7fa;
}

.preview-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.preview-item:hover img {
  transform: scale(1.05);
}

.preview-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 8px;
  background: linear-gradient(transparent, rgba(0,0,0,0.6));
  display: flex;
  justify-content: flex-end;
  opacity: 0;
  transition: opacity 0.3s;
}

.preview-item:hover .preview-overlay {
  opacity: 1;
}

/* 图库区域 */
.gallery-section {
  margin-top: 20px;
  background: transparent;
  border-radius: 8px;
  border: 1px solid #ebeef5;
}

.gallery-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  cursor: pointer;
  user-select: none;
  border-bottom: 1px solid #ebeef5;
  position: sticky;
  top: 0;
  background: #fff;
  z-index: 10;
  border-radius: 8px 8px 0 0;
}

.gallery-header:hover {
  background: #f5f7fa;
}

.gallery-header span {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
}

.gallery-header .el-icon:last-child {
  transition: transform 0.3s;
}

.gallery-header .el-icon.is-expanded {
  transform: rotate(180deg);
}

.gallery-content {
  padding: 16px;
}

.gallery-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 40px;
  color: #909399;
}

.gallery-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 8px;
}

.gallery-item {
  position: relative;
  border-radius: 6px;
  overflow: hidden;
  cursor: pointer;
  aspect-ratio: 1;
  background: #f5f7fa;
}

.gallery-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.gallery-item:hover img {
  transform: scale(1.1);
}

.gallery-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 4px 8px;
  background: linear-gradient(transparent, rgba(0,0,0,0.6));
  opacity: 0;
  transition: opacity 0.3s;
}

.gallery-item:hover .gallery-overlay {
  opacity: 1;
}

.gallery-date {
  color: #fff;
  font-size: 12px;
}

.gallery-pagination {
  margin-top: 16px;
  display: flex;
  justify-content: center;
}
</style>
