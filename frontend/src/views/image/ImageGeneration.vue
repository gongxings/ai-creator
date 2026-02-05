<template>
  <div class="image-generation">
    <el-card class="header-card">
      <h2>AI图片生成</h2>
      <p class="subtitle">使用AI技术，将文字描述转换为精美图片</p>
    </el-card>

    <el-row :gutter="20">
      <!-- 左侧：输入区域 -->
      <el-col :xs="24" :lg="12">
        <el-card class="input-card">
          <template #header>
            <div class="card-header">
              <span>图片描述</span>
              <el-button type="primary" :loading="generating" @click="generateImage">
                <el-icon><Picture /></el-icon>
                生成图片
              </el-button>
            </div>
          </template>

          <el-form :model="form" label-position="top">
            <el-form-item label="描述内容" required>
              <el-input
                v-model="form.prompt"
                type="textarea"
                :rows="6"
                placeholder="请详细描述你想要生成的图片，例如：一只可爱的橘猫坐在窗台上，阳光洒在它身上，背景是城市天际线，写实风格"
                maxlength="1000"
                show-word-limit
              />
            </el-form-item>

            <el-form-item label="图片尺寸">
              <el-select v-model="form.size" placeholder="请选择尺寸">
                <el-option label="1024x1024 (正方形)" value="1024x1024" />
                <el-option label="1024x1792 (竖版)" value="1024x1792" />
                <el-option label="1792x1024 (横版)" value="1792x1024" />
              </el-select>
            </el-form-item>

            <el-form-item label="生成数量">
              <el-slider v-model="form.n" :min="1" :max="4" :marks="{ 1: '1', 2: '2', 3: '3', 4: '4' }" />
            </el-form-item>

            <el-form-item label="图片风格">
              <el-select v-model="form.style" placeholder="请选择风格">
                <el-option label="自然" value="natural" />
                <el-option label="生动" value="vivid" />
              </el-select>
            </el-form-item>

            <el-form-item label="画质">
              <el-radio-group v-model="form.quality">
                <el-radio label="standard">标准</el-radio>
                <el-radio label="hd">高清</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 历史记录 -->
        <el-card class="history-card" style="margin-top: 20px">
          <template #header>
            <span>最近生成</span>
          </template>
          <el-empty v-if="historyList.length === 0" description="暂无历史记录" />
          <div v-else class="history-list">
            <div
              v-for="item in historyList"
              :key="item.id"
              class="history-item"
              @click="loadHistory(item)"
            >
              <el-image
                :src="item.images[0]"
                fit="cover"
                class="history-thumbnail"
                :preview-src-list="item.images"
              />
              <div class="history-info">
                <div class="history-prompt">{{ item.prompt }}</div>
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
            <span>生成结果</span>
          </template>

          <el-empty v-if="generatedImages.length === 0" description="请输入描述并点击生成图片" />
          
          <div v-else class="image-grid">
            <div v-for="(image, index) in generatedImages" :key="index" class="image-item">
              <el-image
                :src="image"
                fit="contain"
                :preview-src-list="generatedImages"
                :initial-index="index"
              />
              <div class="image-actions">
                <el-button size="small" @click="downloadImage(image)">
                  <el-icon><Download /></el-icon>
                  下载
                </el-button>
                <el-button size="small" @click="saveToHistory(image)">
                  <el-icon><Star /></el-icon>
                  收藏
                </el-button>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Picture, Download, Star } from '@element-plus/icons-vue'
import request from '@/api/request'

interface ImageForm {
  prompt: string
  size: string
  n: number
  style: string
  quality: string
}

interface HistoryItem {
  id: number
  prompt: string
  images: string[]
  created_at: string
}

const form = reactive<ImageForm>({
  prompt: '',
  size: '1024x1024',
  n: 1,
  style: 'vivid',
  quality: 'standard',
})

const generating = ref(false)
const generatedImages = ref<string[]>([])
const historyList = ref<HistoryItem[]>([])
const currentTask = ref<{ id: string; status: string; progress: number } | null>(null)
let pollTimer: number | null = null

// 生成图片
const generateImage = async () => {
  if (!form.prompt.trim()) {
    ElMessage.warning('请输入图片描述')
    return
  }

  generating.value = true
  try {
    const { width, height } = parseSize(form.size)
    const result = await request.post('/v1/image/generate', {
      prompt: form.prompt,
      width,
      height,
      num_images: form.n,
      style: form.style,
    })
    const task = result.data
    currentTask.value = {
      id: task.task_id,
      status: task.status,
      progress: task.progress || 0,
    }
    generatedImages.value = []
    ElMessage.success('图片生成任务已提交')
    startPolling()
    
    // 刷新历史记录
    loadHistory()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.message || '图片生成失败')
  } finally {
    generating.value = false
  }
}

const startPolling = () => {
  if (pollTimer) {
    clearInterval(pollTimer)
  }

  pollTimer = window.setInterval(async () => {
    if (!currentTask.value) return

    try {
      const result = await request.get(`/v1/image/task/${currentTask.value.id}`)
      const task = result.data

      currentTask.value = {
        id: task.task_id,
        status: task.status,
        progress: task.progress || 0,
      }

      if (task.status === 'completed') {
        generatedImages.value = task.images || []
        stopPolling()
        ElMessage.success('图片生成完成')
        loadHistory()
      } else if (task.status === 'failed') {
        stopPolling()
        ElMessage.error('图片生成失败')
      }
    } catch (error) {
      console.error('获取图片任务状态失败', error)
    }
  }, 3000)
}

const stopPolling = () => {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

const parseSize = (size: string) => {
  const [width, height] = size.split('x').map((value) => Number(value))
  return {
    width: Number.isFinite(width) ? width : 1024,
    height: Number.isFinite(height) ? height : 1024,
  }
}

// 下载图片
const downloadImage = (url: string) => {
  const link = document.createElement('a')
  link.href = url
  link.download = `ai-image-${Date.now()}.png`
  link.click()
}

// 保存到历史
const saveToHistory = async (url: string) => {
  ElMessage.success('已收藏')
}

// 加载历史记录
const loadHistory = async (item?: HistoryItem) => {
  if (item) {
    form.prompt = item.prompt
    generatedImages.value = item.images
    return
  }

  try {
    const result = await request.get('/v1/creations', {
      params: {
        content_type: 'image',
        skip: 0,
        limit: 10,
      },
    })
    historyList.value = result.items
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
.image-generation {
  padding: 20px;

  .header-card {
    margin-bottom: 20px;
    text-align: center;

    h2 {
      margin: 0 0 10px 0;
      font-size: 24px;
      color: #303133;
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

  .history-list {
    max-height: 400px;
    overflow-y: auto;

    .history-item {
      display: flex;
      gap: 12px;
      padding: 12px;
      margin-bottom: 12px;
      border: 1px solid #ebeef5;
      border-radius: 4px;
      cursor: pointer;
      transition: all 0.3s;

      &:hover {
        border-color: #409eff;
        background-color: #f5f7fa;
      }

      .history-thumbnail {
        width: 80px;
        height: 80px;
        border-radius: 4px;
        flex-shrink: 0;
      }

      .history-info {
        flex: 1;
        min-width: 0;

        .history-prompt {
          font-size: 14px;
          color: #303133;
          margin-bottom: 8px;
          overflow: hidden;
          text-overflow: ellipsis;
          display: -webkit-box;
          -webkit-line-clamp: 2;
          -webkit-box-orient: vertical;
        }

        .history-time {
          font-size: 12px;
          color: #909399;
        }
      }
    }
  }

  .image-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 20px;

    .image-item {
      border: 1px solid #ebeef5;
      border-radius: 4px;
      overflow: hidden;

      .el-image {
        width: 100%;
        height: 300px;
      }

      .image-actions {
        padding: 12px;
        display: flex;
        gap: 8px;
        justify-content: center;
        background-color: #f5f7fa;
      }
    }
  }
}

@media (max-width: 768px) {
  .image-generation {
    padding: 10px;

    .image-grid {
      grid-template-columns: 1fr;
    }
  }
}
</style>
