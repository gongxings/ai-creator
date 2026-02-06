<template>
  <div class="video-generation">
    <el-card class="header-card">
      <div class="header-content">
        <div class="header-left">
          <h2>AI视频生成</h2>
          <p class="subtitle">使用AI技术，将文字或图片转换为精彩视频</p>
        </div>
      </div>
    </el-card>

    <el-row :gutter="[16, 16]">
      <!-- 左侧：输入区域 -->
      <el-col :xs="24" :sm="24" :md="24" :lg="12">
        <el-card class="input-card">
          <template #header>
            <div class="card-header">
              <span>视频生成</span>
              <el-button type="primary" :loading="generating" @click="generateVideo">
                <el-icon><VideoCamera /></el-icon>
                生成视频
              </el-button>
            </div>
          </template>

          <el-tabs v-model="activeTab" class="custom-tabs">
            <!-- 文本生成视频 -->
            <el-tab-pane label="文本生成视频" name="text">
              <el-form :model="textForm" label-position="top">
                <el-form-item label="视频描述" required>
                  <el-input
                    v-model="textForm.prompt"
                    type="textarea"
                    :rows="6"
                    placeholder="请详细描述你想要生成的视频内容，例如：一只可爱的小猫在花园里追逐蝴蝶，阳光明媚，画面温馨"
                    maxlength="2000"
                    show-word-limit
                  />
                </el-form-item>

                <el-row :gutter="[12, 12]">
                  <el-col :xs="24" :sm="12">
                    <el-form-item label="视频时长">
                      <el-select v-model="textForm.duration" placeholder="请选择时长" style="width: 100%">
                        <el-option label="5秒" :value="5" />
                        <el-option label="10秒" :value="10" />
                        <el-option label="15秒" :value="15" />
                        <el-option label="30秒" :value="30" />
                      </el-select>
                    </el-form-item>
                  </el-col>
                  <el-col :xs="24" :sm="12">
                    <el-form-item label="视频风格">
                      <el-select v-model="textForm.style" placeholder="请选择风格" style="width: 100%">
                        <el-option label="真实" value="realistic" />
                        <el-option label="动画" value="animated" />
                        <el-option label="艺术" value="artistic" />
                      </el-select>
                    </el-form-item>
                  </el-col>
                </el-row>

                <el-form-item label="视频比例">
                  <el-radio-group v-model="textForm.aspect_ratio" class="ratio-group">
                    <el-radio-button label="16:9">
                      <div class="ratio-option">
                        <div class="ratio-icon landscape"></div>
                        <span>横屏 16:9</span>
                      </div>
                    </el-radio-button>
                    <el-radio-button label="9:16">
                      <div class="ratio-option">
                        <div class="ratio-icon portrait"></div>
                        <span>竖屏 9:16</span>
                      </div>
                    </el-radio-button>
                    <el-radio-button label="1:1">
                      <div class="ratio-option">
                        <div class="ratio-icon square"></div>
                        <span>方形 1:1</span>
                      </div>
                    </el-radio-button>
                  </el-radio-group>
                </el-form-item>
              </el-form>
            </el-tab-pane>

            <!-- 图片生成视频 -->
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
                    <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                    <div class="el-upload__text">
                      拖拽图片到此处或<em>点击上传</em>
                    </div>
                    <template #tip>
                      <div class="el-upload__tip">
                        支持 jpg/png 格式，建议尺寸 1920x1080
                      </div>
                    </template>
                  </el-upload>
                </el-form-item>

                <el-form-item label="运动描述">
                  <el-input
                    v-model="imageForm.motion_prompt"
                    type="textarea"
                    :rows="3"
                    placeholder="描述图片中的运动效果，例如：镜头缓慢推进，人物微笑"
                    maxlength="500"
                    show-word-limit
                  />
                </el-form-item>

                <el-form-item label="视频时长">
                  <el-select v-model="imageForm.duration" placeholder="请选择时长" style="width: 100%">
                    <el-option label="5秒" :value="5" />
                    <el-option label="10秒" :value="10" />
                  </el-select>
                </el-form-item>
              </el-form>
            </el-tab-pane>
          </el-tabs>

          <!-- AI服务选择卡片 -->
          <el-card shadow="never" class="model-card">
            <template #header><span>AI服务</span></template>
            
            <el-form-item label="使用模式">
              <el-segmented v-model="aiMode" :options="['API Key', 'Cookie']" block />
            </el-form-item>
            
            <template v-if="aiMode === 'API Key'">
              <el-alert type="info" title="API Key模式" :closable="false">
                <p>使用配置的API Key调用，需消耗积分</p>
              </el-alert>
            </template>
            
            <template v-else>
              <el-form-item label="选择平台">
                <el-select v-model="selectedPlatform" placeholder="选择AI平台" style="width: 100%">
                  <el-option label="豆包 (Doubao)" value="doubao" />
                  <el-option label="通义千问 (Qwen)" value="qwen" />
                  <el-option label="Runway" value="runway" />
                </el-select>
              </el-form-item>
              <el-alert type="success" title="Cookie模式" :closable="false">
                <p>使用已授权账号的免费额度</p>
              </el-alert>
            </template>
          </el-card>
        </el-card>

        <!-- 生成历史 -->
        <el-card class="history-card">
          <template #header>
            <div class="card-header">
              <span>生成历史</span>
              <el-button text type="primary" size="small" @click="loadHistory">刷新</el-button>
            </div>
          </template>
          <el-empty v-if="historyList.length === 0" description="暂无历史记录" />
          <div v-else class="history-list">
            <div
              v-for="item in historyList"
              :key="item.id"
              class="history-item"
              @click="viewVideo(item)"
            >
              <div class="history-thumbnail">
                <el-icon><VideoCamera /></el-icon>
              </div>
              <div class="history-info">
                <div class="history-title">{{ item.title }}</div>
                <div class="history-meta">
                  <el-tag v-if="item.status === 'completed'" type="success" size="small">已完成</el-tag>
                  <el-tag v-else-if="item.status === 'processing'" type="warning" size="small">生成中</el-tag>
                  <el-tag v-else type="danger" size="small">失败</el-tag>
                  <span class="history-time">{{ formatTime(item.created_at) }}</span>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

       <!-- 右侧：预览区域 -->
      <el-col :xs="24" :sm="24" :md="24" :lg="12">
        <el-card class="preview-card">
          <template #header>
            <div class="card-header">
              <span>视频预览</span>
              <el-tag v-if="currentTask && currentTask.status === 'processing'" type="warning">
                生成中 {{ currentTask.progress }}%
              </el-tag>
            </div>
          </template>

          <div v-if="currentTask" class="task-status">
            <div v-if="currentTask.status === 'processing'" class="generating-status">
              <el-progress type="circle" :percentage="currentTask.progress" :width="120" />
              <p>视频生成中，预计还需 {{ currentTask.estimated_time }} 秒...</p>
            </div>

            <el-alert
              v-else-if="currentTask.status === 'failed'"
              title="生成失败"
              type="error"
              :description="currentTask.error"
              :closable="false"
              show-icon
            />

            <div v-else-if="currentTask.status === 'completed'" class="video-player">
              <video :src="currentTask.video_url" controls class="video-element" />
              <div class="video-actions">
                <el-button type="primary" @click="downloadVideo">
                  <el-icon><Download /></el-icon>
                  下载视频
                </el-button>
                <el-button @click="shareVideo">
                  <el-icon><Share /></el-icon>
                  分享
                </el-button>
              </div>
            </div>
          </div>

          <el-empty v-else description="请选择生成方式并点击生成视频" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { VideoCamera, UploadFilled, Download, Share } from '@element-plus/icons-vue'
import type { UploadFile } from 'element-plus'
import request from '@/api/request'

interface TextForm {
  prompt: string
  duration: number
  aspect_ratio: string
  style: string
  platform?: string
}

interface ImageForm {
  image: File | null
  motion_prompt: string
  duration: number
  image_data_url?: string
  platform?: string
}

interface VideoTask {
  id: string
  status: 'processing' | 'completed' | 'failed'
  progress: number
  estimated_time: number
  video_url?: string
  error?: string
}

interface HistoryItem {
  id: number
  title: string
  status: string
  created_at: string
  video_url?: string
}

const activeTab = ref('text')
const generating = ref(false)
const currentTask = ref<VideoTask | null>(null)
const historyList = ref<HistoryItem[]>([])
let pollTimer: number | null = null

// AI模式和平台选择
const aiMode = ref('API Key')  // 'API Key' 或 'Cookie'
const selectedPlatform = ref('doubao')  // 选中的平台

const textForm = reactive<TextForm>({
  prompt: '',
  duration: 10,
  aspect_ratio: '16:9',
  style: 'realistic',
})

const imageForm = reactive<ImageForm>({
  image: null,
  motion_prompt: '',
  duration: 5,
})

// 处理图片上传
const handleImageChange = async (file: UploadFile) => {
  imageForm.image = file.raw as File
  imageForm.image_data_url = await readFileAsDataUrl(file.raw as File)
}

// 生成视频
const generateVideo = async () => {
  if (activeTab.value === 'text') {
    if (!textForm.prompt.trim()) {
      ElMessage.warning('请输入视频描述')
      return
    }
  } else {
    if (!imageForm.image) {
      ElMessage.warning('请上传图片')
      return
    }
  }

  // Cookie模式需要选择平台
  if (aiMode.value === 'Cookie' && !selectedPlatform.value) {
    ElMessage.warning('请选择AI平台')
    return
  }

  generating.value = true
  try {
    let response
    if (activeTab.value === 'text') {
      response = await request.post('/v1/video/text-to-video', {
        text: textForm.prompt,
        background_music: false,
        subtitle: true,
        platform: aiMode.value === 'Cookie' ? selectedPlatform.value : undefined,
      })
    } else {
      const images = imageForm.image_data_url ? [imageForm.image_data_url] : []
      response = await request.post('/v1/video/image-to-video', {
        images,
        transition: 'fade',
        duration_per_image: imageForm.duration,
        platform: aiMode.value === 'Cookie' ? selectedPlatform.value : undefined,
      })
    }

    const task = response.data
    currentTask.value = {
      id: task.task_id,
      status: 'processing',
      progress: 0,
      estimated_time: task.estimated_time || 60,
    }

    ElMessage.success('视频生成任务已提交')
    startPolling()
    loadHistory()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.message || '视频生成失败')
  } finally {
    generating.value = false
  }
}

// 轮询任务状态
const startPolling = () => {
  if (pollTimer) {
    clearInterval(pollTimer)
  }

  pollTimer = window.setInterval(async () => {
    if (!currentTask.value) return

    try {
      const result = await request.get(`/v1/video/task/${currentTask.value.id}`)
      const data = result.data

      currentTask.value = {
        ...currentTask.value,
        status: data.status,
        progress: data.progress || 0,
        estimated_time: data.estimated_time || 0,
        video_url: data.video_url,
        error: data.error,
      }

      if (data.status === 'completed' || data.status === 'failed') {
        stopPolling()
        if (data.status === 'completed') {
          ElMessage.success('视频生成完成')
          loadHistory()
        } else {
          ElMessage.error('视频生成失败')
        }
      }
    } catch (error) {
      console.error('获取任务状态失败', error)
    }
  }, 3000)
}

const readFileAsDataUrl = (file: File) => new Promise<string>((resolve, reject) => {
  const reader = new FileReader()
  reader.onload = () => resolve(reader.result as string)
  reader.onerror = () => reject(new Error('读取图片失败'))
  reader.readAsDataURL(file)
})

const stopPolling = () => {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

// 查看视频
const viewVideo = (item: HistoryItem) => {
  if (item.status === 'completed' && item.video_url) {
    currentTask.value = {
      id: item.id.toString(),
      status: 'completed',
      progress: 100,
      estimated_time: 0,
      video_url: item.video_url,
    }
  }
}

// 下载视频
const downloadVideo = () => {
  if (currentTask.value?.video_url) {
    const link = document.createElement('a')
    link.href = currentTask.value.video_url
    link.download = `ai-video-${Date.now()}.mp4`
    link.click()
  }
}

// 分享视频
const shareVideo = async () => {
  if (!currentTask.value?.video_url) {
    ElMessage.warning('暂无可分享的视频链接')
    return
  }

  try {
    await navigator.clipboard.writeText(currentTask.value.video_url)
    ElMessage.success('视频链接已复制，可直接分享')
  } catch (error) {
    ElMessage.warning('复制失败，请手动复制链接')
  }
}

// 加载历史记录
const loadHistory = async () => {
  try {
    const response = await request.get('/v1/creations', {
      params: {
        content_type: 'video',
        skip: 0,
        limit: 10,
      },
    })
    historyList.value = response.items
  } catch (error) {
    console.error('加载历史记录失败', error)
  }
}

// 格式化时间
const formatTime = (time: string) => {
  const date = new Date(time)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  return date.toLocaleDateString()
}

onMounted(() => {
  loadHistory()
})

onUnmounted(() => {
  stopPolling()
})
</script>

<style scoped lang="scss">
// Variables
$primary-color: #409eff;
$success-color: #67c23a;
$border-color: #edf2f7;
$bg-color: #f8fbff;
$text-primary: #1f2937;
$text-secondary: #606266;
$text-tertiary: #909399;
$shadow-light: 0 8px 24px rgba(15, 23, 42, 0.04);
$shadow-hover: 0 12px 32px rgba(15, 23, 42, 0.08);
$border-radius-lg: 14px;
$border-radius-md: 12px;
$border-radius-sm: 10px;
$transition: all 0.3s ease-out;

.video-generation {
  padding: 20px;
  background: linear-gradient(180deg, $bg-color 0%, #ffffff 40%);
  min-height: 100vh;

  :deep(.el-card) {
    border-radius: $border-radius-lg;
    border: 1px solid $border-color;
    box-shadow: $shadow-light;
    transition: $transition;

    &:hover {
      box-shadow: $shadow-hover;
    }

    .el-card__header {
      padding: 16px 20px;
      border-bottom: 1px solid $border-color;
      background: #f9fafb;
    }

    .el-card__body {
      padding: 20px;
    }
  }

  :deep(.el-form-item) {
    margin-bottom: 16px;

    &:last-child {
      margin-bottom: 0;
    }
  }

  :deep(.el-input) {
    &.is-disabled {
      .el-input__wrapper {
        background-color: #f5f7fa;
      }
    }
  }

  :deep(.el-select) {
    width: 100%;
  }

  :deep(.el-tabs) {
    .el-tabs__header {
      margin-bottom: 16px;
    }

    .el-tabs__nav {
      border-bottom: 2px solid $border-color;
    }

    .el-tabs__item {
      color: $text-secondary;
      border-color: transparent;

      &.is-active {
        color: $primary-color;
      }

      &:hover {
        color: $primary-color;
      }
    }
  }

  // Header Card
  .header-card {
    margin-bottom: 24px;
    text-align: center;
    background: linear-gradient(135deg, #eff6ff 0%, #f5f3ff 100%);
    border: none;
    box-shadow: 0 4px 20px rgba(15, 23, 42, 0.06);

    .header-content {
      padding: 24px 16px;
    }

    .header-left {
      h2 {
        margin: 0 0 8px 0;
        font-size: clamp(20px, 5vw, 28px);
        color: $text-primary;
        font-weight: 600;
        letter-spacing: -0.3px;
      }

      .subtitle {
        margin: 0;
        color: $text-tertiary;
        font-size: clamp(12px, 3vw, 14px);
        font-weight: 400;
      }
    }
  }

  // Card Header
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
    gap: 12px;
    flex-wrap: wrap;

    span {
      font-size: 16px;
      font-weight: 500;
      color: $text-primary;
      white-space: nowrap;
    }

    :deep(.el-button) {
      white-space: nowrap;
    }
  }

  // Input Card
  .input-card {
    margin-bottom: 20px;
    transition: $transition;

    :deep(.custom-tabs) {
      .el-tabs__header {
        margin-bottom: 20px;
      }
    }

    .model-card {
      margin-top: 20px;
      background-color: #f9fafb;

      :deep(.el-card__header) {
        background-color: transparent;
        padding: 12px 0;
      }

      :deep(.el-card__body) {
        padding: 16px 0;
      }

      :deep(.el-alert) {
        margin-top: 12px;
        border-radius: 8px;
      }
    }
  }

  // Progress Info
  .progress-info {
    padding: 24px;
    text-align: center;
    background: #f9fafb;
    border-radius: $border-radius-md;
    margin: 16px 0;

    p {
      margin: 12px 0 0 0;
      text-align: center;
      color: $text-secondary;
      font-size: 14px;
    }
  }

  // Video Player
  .video-player {
    padding-top: 8px;
    animation: fadeIn 0.4s ease-out;

    .video-element {
      width: 100%;
      max-height: 500px;
      background-color: #000;
      border-radius: $border-radius-md;
      display: block;
      margin: 0 auto;
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
    }

    .video-actions {
      margin-top: 20px;
      display: flex;
      gap: 12px;
      justify-content: center;
      flex-wrap: wrap;

      :deep(.el-button) {
        min-width: 120px;
      }
    }
  }

  // Task Status
  .task-status {
    padding: 16px 0;

    .generating-status {
      padding: 32px 16px;
      text-align: center;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 16px;

      p {
        margin: 0;
        color: $text-secondary;
        font-size: 14px;
      }
    }

    :deep(.el-alert) {
      border-radius: 8px;
    }
  }

  // History Card
  .history-card {
    margin-bottom: 0;
  }

  .history-list {
    max-height: 450px;
    overflow-y: auto;
    padding: 4px 0;

    &::-webkit-scrollbar {
      width: 6px;
    }

    &::-webkit-scrollbar-track {
      background: transparent;
    }

    &::-webkit-scrollbar-thumb {
      background: #ccc;
      border-radius: 3px;

      &:hover {
        background: #999;
      }
    }

    .history-item {
      display: flex;
      background: #fff;
      gap: 12px;
      padding: 12px;
      margin-bottom: 12px;
      border: 1px solid $border-color;
      border-radius: $border-radius-sm;
      cursor: pointer;
      transition: $transition;
      align-items: flex-start;

      &:hover {
        border-color: $primary-color;
        background-color: #f1f5f9;
        box-shadow: 0 4px 12px rgba(64, 158, 255, 0.1);
        transform: translateY(-2px);
      }

      .history-thumbnail {
        width: 80px;
        height: 80px;
        min-width: 80px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #f5f7fa 0%, #e9ecf1 100%);
        border-radius: 8px;
        flex-shrink: 0;

        .el-icon {
          font-size: 36px;
          color: $primary-color;
          transition: $transition;
        }
      }

      .history-info {
        flex: 1;
        min-width: 0;
        display: flex;
        flex-direction: column;
        justify-content: space-between;

        .history-title {
          font-size: 14px;
          color: $text-primary;
          margin-bottom: 8px;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
          font-weight: 500;
        }

        .history-meta {
          display: flex;
          gap: 8px;
          align-items: center;
          flex-wrap: wrap;

          :deep(.el-tag) {
            border-radius: 4px;
            padding: 2px 8px;
            font-size: 12px;
          }
        }

        .history-time {
          font-size: 12px;
          color: $text-tertiary;
        }
      }
    }
  }

  // Animations
  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateY(8px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  @keyframes slideInLeft {
    from {
      opacity: 0;
      transform: translateX(-12px);
    }
    to {
      opacity: 1;
      transform: translateX(0);
    }
  }
}

// Responsive Design - Tablet (768px - 1024px)
@media (max-width: 1024px) {
  .video-generation {
    padding: 16px;

    .header-card {
      margin-bottom: 20px;

      .header-content {
        padding: 20px 12px;
      }
    }

    .video-player {
      .video-element {
        max-height: 400px;
      }
    }

    .history-list {
      max-height: 350px;
    }
  }
}

// Responsive Design - Large Mobile (480px - 768px)
@media (max-width: 768px) {
  .video-generation {
    padding: 12px;
    background: linear-gradient(180deg, $bg-color 0%, #ffffff 60%);

    :deep(.el-card) {
      border-radius: 12px;

      .el-card__header {
        padding: 14px 16px;
      }

      .el-card__body {
        padding: 16px;
      }
    }

    .header-card {
      margin-bottom: 16px;
      box-shadow: 0 2px 12px rgba(15, 23, 42, 0.04);

      .header-content {
        padding: 16px 12px;
      }

      h2 {
        font-size: 20px;
      }

      .subtitle {
        font-size: 12px;
      }
    }

    .card-header {
      gap: 8px;

      span {
        font-size: 15px;
      }

      :deep(.el-button) {
        padding: 6px 12px;
        font-size: 13px;
      }
    }

    .input-card {
      margin-bottom: 16px;

      :deep(.el-form-item) {
        margin-bottom: 14px;
      }

      .model-card {
        margin-top: 16px;
      }
    }

    .video-player {
      padding-top: 4px;

      .video-element {
        max-height: 300px;
        border-radius: 10px;
      }

      .video-actions {
        gap: 8px;
        margin-top: 16px;

        :deep(.el-button) {
          flex: 1;
          min-width: 100px;
          padding: 8px 12px;
          font-size: 13px;
        }
      }
    }

    .task-status {
      padding: 12px 0;

      .generating-status {
        padding: 24px 12px;
        gap: 12px;

        :deep(.el-progress) {
          --ep-progress-bg-color: $primary-color;
        }
      }
    }

    .history-card {
      margin-top: 16px;
    }

    .history-list {
      max-height: 400px;
      padding: 2px 0;

      .history-item {
        gap: 10px;
        padding: 10px;
        margin-bottom: 10px;
        border-radius: 8px;

        &:hover {
          transform: translateY(-1px);
        }

        .history-thumbnail {
          width: 72px;
          height: 72px;
          min-width: 72px;
          border-radius: 6px;

          .el-icon {
            font-size: 28px;
          }
        }

        .history-info {
          .history-title {
            font-size: 13px;
            margin-bottom: 6px;
          }

          .history-meta {
            gap: 6px;

            :deep(.el-tag) {
              padding: 1px 6px;
              font-size: 11px;
            }
          }

          .history-time {
            font-size: 11px;
          }
        }
      }
    }
  }
}

// Responsive Design - Small Mobile (320px - 480px)
@media (max-width: 480px) {
  .video-generation {
    padding: 8px;

    :deep(.el-card) {
      border-radius: 10px;
      border: 1px solid $border-color;

      .el-card__header {
        padding: 12px 14px;
      }

      .el-card__body {
        padding: 14px;
      }
    }

    .header-card {
      margin-bottom: 12px;

      .header-content {
        padding: 12px 10px;
      }

      h2 {
        font-size: 18px;
        margin-bottom: 6px;
      }

      .subtitle {
        font-size: 11px;
        line-height: 1.4;
      }
    }

    .card-header {
      flex-direction: column;
      align-items: flex-start;
      gap: 10px;

      span {
        font-size: 14px;
      }

      :deep(.el-button) {
        width: 100%;
        padding: 6px 12px;
        font-size: 12px;
      }
    }

    :deep(.el-form-item) {
      margin-bottom: 12px;

      :deep(.el-form-item__label) {
        font-size: 13px;
        padding-bottom: 8px;
      }
    }

    :deep(.el-input) {
      :deep(.el-input__wrapper) {
        padding: 6px 10px;
      }

      :deep(textarea) {
        font-size: 13px;
        padding: 6px;
      }
    }

    :deep(.el-select) {
      :deep(.el-input) {
        font-size: 13px;
      }
    }

    :deep(.el-tabs) {
      :deep(.el-tabs__header) {
        margin-bottom: 12px;
      }

      :deep(.el-tabs__item) {
        font-size: 13px;
        padding: 0 12px;
      }

      :deep(.el-tabs__content) {
        padding: 0;
      }
    }

    .input-card {
      margin-bottom: 12px;

      .model-card {
        margin-top: 12px;
      }
    }

    .video-player {
      padding-top: 0;

      .video-element {
        max-height: 240px;
        border-radius: 8px;
      }

      .video-actions {
        flex-direction: column;
        gap: 8px;
        margin-top: 12px;

        :deep(.el-button) {
          width: 100%;
          padding: 8px 12px;
          font-size: 12px;
        }
      }
    }

    .task-status {
      padding: 8px 0;

      .generating-status {
        padding: 20px 8px;
        gap: 10px;

        p {
          font-size: 12px;
        }
      }
    }

    .history-card {
      margin-top: 12px;
    }

    .history-list {
      max-height: 350px;

      .history-item {
        gap: 8px;
        padding: 8px;
        margin-bottom: 8px;

        .history-thumbnail {
          width: 60px;
          height: 60px;
          min-width: 60px;

          .el-icon {
            font-size: 24px;
          }
        }

        .history-info {
          .history-title {
            font-size: 12px;
            margin-bottom: 4px;
          }

          .history-meta {
            gap: 4px;

            :deep(.el-tag) {
              padding: 0 4px;
              font-size: 10px;
              height: auto;
              line-height: 1.2;
            }
          }

          .history-time {
            font-size: 10px;
            margin-top: 2px;
          }
        }
      }
    }

    :deep(.el-radio-group) {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    :deep(.el-radio-button) {
      flex: 1;
      margin-right: 0;

      :deep(.el-radio__label) {
        font-size: 12px;
      }
    }

    .ratio-group {
      display: flex;
      flex-direction: column;
    }
  }
}

// Ultra Small Mobile (< 320px)
@media (max-width: 320px) {
  .video-generation {
    padding: 6px;

    :deep(.el-card) {
      border-radius: 8px;

      .el-card__header {
        padding: 10px 12px;
      }

      .el-card__body {
        padding: 12px;
      }
    }

    .header-card {
      h2 {
        font-size: 16px;
      }

      .subtitle {
        font-size: 10px;
      }
    }

    .video-player {
      .video-element {
        max-height: 200px;
      }
    }
  }
}
</style>
