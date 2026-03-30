<template>
  <div class="video-generation">
    <div class="main-content">
      <!-- 左侧：参数面板 -->
      <div class="left-panel">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>AI 视频生成</span>
              <el-button type="primary" :loading="generating" @click="generateVideo">
                <el-icon><VideoPlay /></el-icon>
                生成
              </el-button>
            </div>
          </template>

          <el-form label-position="top">
            <el-form-item label="选择模型" required>
              <el-select v-model="selectedModelId" placeholder="请选择视频生成模型" style="width: 100%">
                <el-option
                  v-for="model in videoModels"
                  :key="model.id"
                  :label="model.name"
                  :value="model.id"
                />
              </el-select>
              <div v-if="!videoModels.length" class="model-hint">
                暂无可用的视频生成模型，请先在 <router-link to="/settings">设置</router-link> 中添加支持视频生成的模型
              </div>
            </el-form-item>
          </el-form>

          <el-tabs v-model="activeTab">
            <el-tab-pane label="文本生成视频" name="text">
              <el-form :model="textForm" label-position="top">
                <el-form-item label="视频描述" required>
                  <el-input 
                    v-model="textForm.prompt" 
                    type="textarea" 
                    :rows="6" 
                    maxlength="2000" 
                    show-word-limit
                    placeholder="请描述你想生成的视频，例如：一只橘猫坐在窗台上看夕阳，阳光透过窗户洒在猫身上"
                  />
                </el-form-item>
                <el-row :gutter="12">
                  <el-col :span="12">
                    <el-form-item label="时长">
                      <el-select v-model="textForm.duration" style="width: 100%">
                        <el-option label="5秒" :value="5" />
                        <el-option label="10秒" :value="10" />
                        <el-option label="15秒" :value="15" />
                        <el-option label="30秒" :value="30" />
                      </el-select>
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="画幅">
                      <el-select v-model="textForm.aspect_ratio" style="width: 100%">
                        <el-option label="16:9" value="16:9" />
                        <el-option label="9:16" value="9:16" />
                        <el-option label="1:1" value="1:1" />
                      </el-select>
                    </el-form-item>
                  </el-col>
                </el-row>
              </el-form>
            </el-tab-pane>

            <el-tab-pane label="图片生成视频" name="image">
              <el-form :model="imageForm" label-position="top">
                <el-form-item label="上传图片" required>
                  <el-upload 
                    class="upload-area" 
                    drag 
                    :auto-upload="false" 
                    :on-change="handleImageChange" 
                    :limit="1" 
                    accept="image/*"
                  >
                    <template v-if="!imageForm.image_data_url">
                      <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
                      <div class="el-upload__text">拖拽图片到此处或点击上传</div>
                    </template>
                    <template v-else>
                      <img :src="imageForm.image_data_url" class="preview-image" />
                    </template>
                  </el-upload>
                </el-form-item>
                <el-form-item label="运动描述">
                  <el-input 
                    v-model="imageForm.motion_prompt" 
                    type="textarea" 
                    :rows="3" 
                    maxlength="500" 
                    show-word-limit
                    placeholder="描述图片中元素的运动方式"
                  />
                </el-form-item>
              </el-form>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </div>

      <!-- 右侧：预览区域 -->
      <div class="right-panel">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>生成结果</span>
              <el-button v-if="currentTask?.status === 'completed'" type="primary" link @click="downloadVideo">
                <el-icon><Download /></el-icon>
                下载
              </el-button>
            </div>
          </template>

          <!-- Loading 状态 -->
          <div v-if="generating" class="loading-container">
            <div class="loading-animation">
              <div class="loading-spinner"></div>
            </div>
            <p class="loading-text">视频生成中...</p>
            <p class="loading-hint">AI 正在生成你的创意，请稍候</p>
            <el-progress v-if="currentTask?.progress" :percentage="currentTask.progress" :stroke-width="8" style="width: 60%; margin-top: 20px;" />
          </div>

          <!-- 视频预览 -->
          <div v-else-if="currentTask?.status === 'completed' && currentTask.video_url" class="video-preview">
            <video :src="currentTask.video_url" controls class="video-element" />
          </div>

          <!-- 失败状态 -->
          <div v-else-if="currentTask?.status === 'failed'" class="error-container">
            <el-alert type="error" :title="currentTask.error || '生成失败'" :closable="false" />
          </div>

          <!-- 处理中状态 -->
          <div v-else-if="currentTask?.status === 'processing'" class="processing-container">
            <el-progress v-if="currentTask.progress" :percentage="currentTask.progress" :stroke-width="10" />
            <p class="processing-text">视频处理中...</p>
          </div>

          <!-- 空状态 -->
          <el-empty v-else description="请输入提示词，点击生成按钮开始创作" />
        </el-card>
      </div>
    </div>

    <!-- 底部：视频库 -->
    <div class="gallery-section">
      <div class="gallery-header" @click="toggleGallery">
        <span>
          <el-icon><VideoCamera /></el-icon>
          我的视频库
          <el-tag size="small" type="info">{{ galleryVideos.length }}</el-tag>
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
          
          <div v-else-if="galleryVideos.length" class="gallery-grid">
            <div 
              v-for="item in galleryVideos" 
              :key="item.id" 
              class="gallery-item"
              @click="previewVideo(item)"
            >
              <video :src="item.url" />
              <div class="gallery-overlay">
                <el-icon><VideoPlay /></el-icon>
                <span class="gallery-date">{{ formatDate(item.created_at) }}</span>
              </div>
            </div>
          </div>
          
          <el-empty v-else description="暂无视频" :image-size="60" />
          
          <div v-if="galleryVideos.length" class="gallery-pagination">
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

    <!-- 视频预览对话框 -->
    <el-dialog v-model="previewVisible" width="80%" :show-close="true" center>
      <video v-if="previewUrl" :src="previewUrl" controls style="width: 100%" />
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled, VideoPlay, Download, VideoCamera, ArrowDown, Loading } from '@element-plus/icons-vue'
import type { UploadFile } from 'element-plus'
import request from '@/api/request'
import { getAIModels } from '@/api/models'
import type { AIModel } from '@/types'

interface TextForm { prompt: string; duration: number; aspect_ratio: string; style: string }
interface ImageForm { image: File | null; motion_prompt: string; duration: number; image_data_url?: string }
interface VideoTask { id: string; status: 'processing' | 'completed' | 'failed'; progress: number; video_url?: string; error?: string }

interface GalleryItem {
  id: number
  url: string
  prompt: string
  created_at: string
}

const activeTab = ref('text')
const generating = ref(false)
const currentTask = ref<VideoTask | null>(null)
const videoModels = ref<AIModel[]>([])
const selectedModelId = ref<number | undefined>(undefined)
let pollTimer: ReturnType<typeof setInterval> | null = null

const textForm = reactive<TextForm>({ prompt: '', duration: 10, aspect_ratio: '16:9', style: 'realistic' })
const imageForm = reactive<ImageForm>({ image: null, motion_prompt: '', duration: 5 })

// 视频库相关
const galleryExpanded = ref(true)
const galleryLoading = ref(false)
const galleryVideos = ref<GalleryItem[]>([])
const galleryPage = ref(1)
const galleryPageSize = 12
const galleryTotal = ref(0)

// 预览相关
const previewVisible = ref(false)
const previewUrl = ref('')

const loadVideoModels = async () => {
  try {
    const res = await getAIModels('video')
    videoModels.value = Array.isArray(res) ? res : (res as any).data || []
    if (videoModels.value.length && !selectedModelId.value) {
      selectedModelId.value = videoModels.value[0].id
    }
  } catch {
    ElMessage.error('加载视频模型失败')
  }
}

const readFileAsDataUrl = (file: File) =>
  new Promise<string>((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(reader.result as string)
    reader.onerror = () => reject(new Error('读取图片失败'))
    reader.readAsDataURL(file)
  })

const handleImageChange = async (file: UploadFile) => {
  imageForm.image = file.raw as File
  imageForm.image_data_url = await readFileAsDataUrl(file.raw as File)
}

const stopPolling = () => {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

const generateVideo = async () => {
  if (!selectedModelId.value) {
    ElMessage.warning('请选择模型')
    return
  }
  if (activeTab.value === 'text' && !textForm.prompt.trim()) {
    ElMessage.warning('请输入视频描述')
    return
  }
  if (activeTab.value === 'image' && !imageForm.image) {
    ElMessage.warning('请上传图片')
    return
  }

  generating.value = true
  currentTask.value = null
  stopPolling()

  try {
    const response =
      activeTab.value === 'text'
        ? await request.post('/v1/video/text-to-video', {
            model_id: selectedModelId.value,
            text: textForm.prompt,
            background_music: false,
            subtitle: true,
          })
        : await request.post('/v1/video/image-to-video', {
            model_id: selectedModelId.value,
            images: imageForm.image_data_url ? [imageForm.image_data_url] : [],
            transition: 'fade',
            duration_per_image: imageForm.duration,
          })

    const task = response.data
    currentTask.value = { id: task.task_id, status: 'processing', progress: 0 }
    ElMessage.success('任务已提交')
    
    pollTimer = setInterval(async () => {
      if (!currentTask.value) return
      try {
        const result = await request.get(`/v1/video/task/${currentTask.value.id}`)
        const data = result.data
        currentTask.value = {
          ...currentTask.value,
          status: data.status,
          progress: data.progress || 0,
          video_url: data.video_url,
          error: data.error,
        }
        if (data.status === 'completed' || data.status === 'failed') {
          stopPolling()
          generating.value = false
          if (data.status === 'completed') {
            ElMessage.success('视频生成完成')
            loadGallery()
          } else {
            ElMessage.error(data.error || '视频生成失败')
          }
        }
      } catch (e) {
        console.error('Polling error:', e)
      }
    }, 3000)
  } catch (error: any) {
    generating.value = false
    ElMessage.error(error.response?.data?.message || '视频生成失败')
  }
}

// 视频库相关
const toggleGallery = () => {
  galleryExpanded.value = !galleryExpanded.value
  if (galleryExpanded.value && !galleryVideos.value.length) {
    loadGallery()
  }
}

const loadGallery = async () => {
  galleryLoading.value = true
  try {
    const res = await request.get('/v1/video/gallery', {
      params: {
        page: galleryPage.value,
        page_size: galleryPageSize,
      }
    })
    galleryVideos.value = res.data.items || []
    galleryTotal.value = res.data.total || 0
  } catch (e: any) {
    ElMessage.error('加载视频库失败')
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
const previewVideo = (item: GalleryItem) => {
  previewUrl.value = item.url
  previewVisible.value = true
}

const downloadVideo = async () => {
  if (!currentTask.value?.video_url) return
  try {
    const response = await fetch(currentTask.value.video_url)
    const blob = await response.blob()
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = `video_${Date.now()}.mp4`
    link.click()
    URL.revokeObjectURL(link.href)
  } catch {
    window.open(currentTask.value.video_url, '_blank')
  }
}

onMounted(() => {
  loadVideoModels()
  loadGallery()
})

onUnmounted(() => {
  stopPolling()
})
</script>

<style scoped>
.video-generation {
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

.upload-area {
  width: 100%;
}

.upload-area :deep(.el-upload-dragger) {
  padding: 20px;
}

.preview-image {
  width: 100%;
  max-height: 200px;
  object-fit: contain;
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

/* 视频预览 */
.video-preview {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #000;
  border-radius: 8px;
  overflow: hidden;
}

.video-element {
  width: 100%;
  max-height: 100%;
  object-fit: contain;
}

/* 错误状态 */
.error-container {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 处理中状态 */
.processing-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
}

.processing-text {
  color: #909399;
  font-size: 14px;
}

/* 视频库区域 */
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
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 8px;
}

.gallery-item {
  position: relative;
  border-radius: 6px;
  overflow: hidden;
  cursor: pointer;
  aspect-ratio: 16/9;
  background: #f5f7fa;
}

.gallery-item video {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.gallery-item:hover video {
  transform: scale(1.05);
}

.gallery-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 8px;
  background: linear-gradient(transparent, rgba(0,0,0,0.6));
  display: flex;
  align-items: center;
  gap: 8px;
  opacity: 0;
  transition: opacity 0.3s;
}

.gallery-item:hover .gallery-overlay {
  opacity: 1;
}

.gallery-overlay .el-icon {
  color: #fff;
  font-size: 16px;
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
