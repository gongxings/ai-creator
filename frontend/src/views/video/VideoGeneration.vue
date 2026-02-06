<template>
  <div class="video-generation">
    <el-card class="header-card">
      <h2>AI视频生成</h2>
      <p class="subtitle">使用AI技术，将文字或图片转换为精彩视频</p>
    </el-card>

    <el-row :gutter="20">
      <!-- 左侧：输入区域 -->
      <el-col :xs="24" :lg="12">
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

          <el-form label-position="top">

          <el-tabs v-model="activeTab">
            <!-- 文本生成视频 -->
            <el-tab-pane label="文本生成视频" name="text">
              <el-form :model="textForm" label-position="top">
                <el-form-item label="视频描述" required>
                  <el-input
                    v-model="textForm.prompt"
                    type="textarea"
                    :rows="8"
                    placeholder="请详细描述你想要生成的视频内容，例如：一只可爱的小猫在花园里追逐蝴蝶，阳光明媚，画面温馨"
                    maxlength="2000"
                    show-word-limit
                  />
                </el-form-item>

                <el-form-item label="视频时长">
                  <el-select v-model="textForm.duration" placeholder="请选择时长">
                    <el-option label="5秒" :value="5" />
                    <el-option label="10秒" :value="10" />
                    <el-option label="15秒" :value="15" />
                    <el-option label="30秒" :value="30" />
                  </el-select>
                </el-form-item>

                <el-form-item label="视频比例">
                  <el-radio-group v-model="textForm.aspect_ratio">
                    <el-radio label="16:9">横屏 (16:9)</el-radio>
                    <el-radio label="9:16">竖屏 (9:16)</el-radio>
                    <el-radio label="1:1">方形 (1:1)</el-radio>
                  </el-radio-group>
                </el-form-item>

                <el-form-item label="视频风格">
                  <el-select v-model="textForm.style" placeholder="请选择风格">
                    <el-option label="真实" value="realistic" />
                    <el-option label="动画" value="animated" />
                    <el-option label="艺术" value="artistic" />
                  </el-select>
                </el-form-item>
              </el-form>
            </el-tab-pane>

            <!-- 图片生成视频 -->
            <el-tab-pane label="图片生成视频" name="image">
              <el-form :model="imageForm" label-position="top">
                <el-form-item label="上传图片" required>
                  <el-upload
                    class="upload-demo"
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
                    :rows="4"
                    placeholder="描述图片中的运动效果，例如：镜头缓慢推进，人物微笑"
                    maxlength="500"
                    show-word-limit
                  />
                </el-form-item>

                <el-form-item label="视频时长">
                  <el-select v-model="imageForm.duration" placeholder="请选择时长">
                    <el-option label="5秒" :value="5" />
                    <el-option label="10秒" :value="10" />
                  </el-select>
                </el-form-item>
              </el-form>
            </el-tab-pane>
          </el-tabs>

          <!-- AI服务选择卡片 -->
          <el-card shadow="never" class="model-card" style="margin-top: 20px">
            <template #header><span>AI服务</span></template>
            
            <!-- 选择模式 -->
            <el-form-item label="使用模式" prop="aiMode">
              <el-segmented v-model="aiMode" :options="['API Key', 'Cookie']" block />
            </el-form-item>
            
            <!-- API Key 模式 -->
            <template v-if="aiMode === 'API Key'">
              <el-alert type="info" title="API Key模式说明" :closable="false" style="margin-bottom: 12px">
                <p>使用配置的API Key调用官方API，需要消耗积分</p>
              </el-alert>
            </template>
            
            <!-- Cookie 模式 -->
            <template v-else>
              <el-form-item label="选择平台" prop="selectedPlatform">
                <el-select v-model="selectedPlatform" placeholder="选择AI平台" style="width: 100%">
                  <el-option label="豆包 (Doubao)" value="doubao" />
                  <el-option label="通义千问 (Qwen)" value="qwen" />
                  <el-option label="Claude" value="claude" />
                </el-select>
              </el-form-item>
              <el-alert type="success" title="Cookie模式说明" :closable="false" style="margin-bottom: 12px">
                <p>使用你已授权的账号免费额度，无需消耗积分</p>
              </el-alert>
            </template>
          </el-card>
        </el-form>
      </div>
    </el-card>

    <!-- 生成历史 -->
    <el-card class="history-card" style="margin-top: 20px">
      <template #header>
        <span>生成历史</span>
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
            <div class="history-status">
              <el-tag v-if="item.status === 'completed'" type="success" size="small">
                已完成
              </el-tag>
              <el-tag v-else-if="item.status === 'processing'" type="warning" size="small">
                生成中
              </el-tag>
              <el-tag v-else type="danger" size="small">失败</el-tag>
            </div>
            <div class="history-time">{{ formatTime(item.created_at) }}</div>
          </div>
        </div>
      </div>
    </el-card>
      </el-col>

      <!-- 右侧：预览区域 -->
      <el-col :xs="24" :lg="12">
        <el-card class="preview-card">
          <template #header>
            <span>视频预览</span>
          </template>

          <div v-if="currentTask" class="task-status">
            <el-alert
              v-if="currentTask.status === 'processing'"
              title="视频生成中"
              type="warning"
              :closable="false"
            >
              <template #default>
                <div class="progress-info">
                  <el-progress :percentage="currentTask.progress" />
                  <p>预计还需 {{ currentTask.estimated_time }} 秒</p>
                </div>
              </template>
            </el-alert>

            <el-alert
              v-else-if="currentTask.status === 'failed'"
              title="生成失败"
              type="error"
              :description="currentTask.error"
              :closable="false"
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
.video-generation {
  padding: 20px;
  background: linear-gradient(180deg, #f8fbff 0%, #ffffff 40%);

  :deep(.el-card) {
    border-radius: 14px;
    border: 1px solid #edf2f7;
    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.04);
  }

  .header-card {
    margin-bottom: 20px;
    text-align: center;
    background: linear-gradient(135deg, #eff6ff 0%, #f5f3ff 100%);

    h2 {
      margin: 0 0 10px 0;
      font-size: 24px;
      color: #1f2937;
    }

    .subtitle {
      margin: 0;
      color: #909399;
      font-size: 14px;
    }
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .input-card {
    .model-card {
      margin-top: 20px;
    }
  }

  .progress-info {
    padding: 20px 0;

    p {
      margin-top: 10px;
      text-align: center;
      color: #606266;
    }
  }

  .video-player {
    padding-top: 8px;
    .video-element {
      width: 100%;
      max-height: 500px;
      background-color: #000;
      border-radius: 12px;
    }

    .video-actions {
      margin-top: 20px;
      display: flex;
      gap: 12px;
      justify-content: center;
    }
  }

  .history-list {
    max-height: 400px;
    overflow-y: auto;

    .history-item {
      display: flex;
      background: #fff;
      gap: 12px;
      padding: 12px;
      margin-bottom: 12px;
      border: 1px solid #ebeef5;
      border-radius: 10px;
      cursor: pointer;
      transition: all 0.3s;

      &:hover {
        border-color: #409eff;
        background-color: #f1f5f9;
      }

      .history-thumbnail {
        width: 80px;
        height: 80px;
        display: flex;
        align-items: center;
        justify-content: center;
        background-color: #f5f7fa;
        border-radius: 4px;
        flex-shrink: 0;

        .el-icon {
          font-size: 32px;
          color: #909399;
        }
      }

      .history-info {
        flex: 1;
        min-width: 0;

        .history-title {
          font-size: 14px;
          color: #303133;
          margin-bottom: 8px;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .history-status {
          margin-bottom: 4px;
        }

        .history-time {
          font-size: 12px;
          color: #909399;
        }
      }
    }
  }
}

@media (max-width: 768px) {
  .video-generation {
    padding: 12px;
  }
}
</style>
