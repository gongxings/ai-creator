<template>
  <div class="image-generation flagship-page page-shell">
    <section class="page-hero image-hero">
      <div class="hero-grid">
        <div class="hero-main">
          <span class="hero-eyebrow">Image Studio</span>
          <h1 class="hero-title">AI图片生成</h1>
          <p class="hero-subtitle">使用AI技术，将文字描述转换为精美图片。</p>
          <div class="hero-actions">
            <el-button type="primary" :loading="generating" @click="generateImage">
              <el-icon><Picture /></el-icon>
              生成图片
            </el-button>
            <el-button @click="loadHistory()">刷新历史</el-button>
          </div>
        </div>
        <div class="hero-panel">
          <div class="hero-panel-title">参数摘要</div>
          <div class="hero-stats">
            <div class="hero-stat">
              <div class="hero-stat-value">{{ form.size }}</div>
              <div class="hero-stat-label">画面尺寸</div>
            </div>
            <div class="hero-stat">
              <div class="hero-stat-value">{{ form.style }}</div>
              <div class="hero-stat-label">视觉风格</div>
            </div>
            <div class="hero-stat">
              <div class="hero-stat-value">{{ form.n }}</div>
              <div class="hero-stat-label">生成数量</div>
            </div>
            <div class="hero-stat">
              <div class="hero-stat-value">{{ form.quality }}</div>
              <div class="hero-stat-label">画质等级</div>
            </div>
          </div>
          <div class="hero-tags">
            <span class="hero-tag">{{ aiMode }}</span>
            <span class="hero-tag" v-if="aiMode === 'Cookie'">{{ selectedPlatform }}</span>
            <span class="hero-tag">实时预览</span>
          </div>
        </div>
      </div>
    </section>

    <section class="page-dashboard">
      <div class="dashboard-grid">
        <div class="dashboard-card">
          <div class="label">历史记录</div>
          <div class="value">{{ historyList.length }}</div>
          <div class="delta">随时回看生成结果</div>
        </div>
        <div class="dashboard-card">
          <div class="label">本次结果</div>
          <div class="value">{{ generatedImages.length }}</div>
          <div class="delta">支持下载与收藏</div>
        </div>
        <div class="dashboard-card">
          <div class="label">任务状态</div>
          <div class="value">{{ currentTask ? '生成中' : '空闲' }}</div>
          <div class="delta">平均等待约 1-2 分钟</div>
        </div>
      </div>
    </section>

    <section class="page-body">
      <div class="main-panel">
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
                    :rows="5"
                    placeholder="请详细描述你想要生成的图片，例如：一只可爱的橘猫坐在窗台上，阳光洒在它身上，背景是城市天际线，写实风格"
                    maxlength="1000"
                    show-word-limit
                  />
                </el-form-item>

                <el-row :gutter="16">
                  <el-col :span="12">
                    <el-form-item label="图片尺寸">
                      <el-select v-model="form.size" placeholder="请选择尺寸" style="width: 100%">
                        <el-option label="1024x1024 (正方形)" value="1024x1024" />
                        <el-option label="1024x1792 (竖版)" value="1024x1792" />
                        <el-option label="1792x1024 (横版)" value="1792x1024" />
                      </el-select>
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="图片风格">
                      <el-select v-model="form.style" placeholder="请选择风格" style="width: 100%">
                        <el-option label="自然" value="natural" />
                        <el-option label="生动" value="vivid" />
                      </el-select>
                    </el-form-item>
                  </el-col>
                </el-row>

                <el-row :gutter="16">
                  <el-col :span="12">
                    <el-form-item label="生成数量">
                      <el-slider v-model="form.n" :min="1" :max="4" :marks="{ 1: '1', 2: '2', 3: '3', 4: '4' }" />
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="画质">
                      <el-radio-group v-model="form.quality">
                        <el-radio label="standard">标准</el-radio>
                        <el-radio label="hd">高清</el-radio>
                      </el-radio-group>
                    </el-form-item>
                  </el-col>
                </el-row>
              </el-form>

              <!-- AI服务选择卡片 -->
              <el-card shadow="never" class="model-card">
                <template #header><span>AI服务</span></template>
                
                <!-- 选择模式 -->
                <el-form-item label="使用模式">
                  <el-segmented v-model="aiMode" :options="['API Key', 'Cookie']" block />
                </el-form-item>
                
                <!-- API Key 模式 -->
                <template v-if="aiMode === 'API Key'">
                  <el-alert type="info" title="API Key模式说明" :closable="false">
                    <p>使用配置的API Key调用官方API，需要消耗积分</p>
                  </el-alert>
                </template>
                
                <!-- Cookie 模式 -->
                <template v-else>
                  <el-form-item label="选择平台">
                    <el-select v-model="selectedPlatform" placeholder="选择AI平台" style="width: 100%">
                      <el-option label="豆包 (Doubao)" value="doubao" />
                      <el-option label="通义千问 (Qwen)" value="qwen" />
                      <el-option label="Midjourney" value="midjourney" />
                    </el-select>
                  </el-form-item>
                  <el-alert type="success" title="Cookie模式说明" :closable="false">
                    <p>使用你已授权的账号免费额度，无需消耗积分</p>
                  </el-alert>
                </template>
              </el-card>
            </el-card>

            <!-- 历史记录 -->
            <el-card class="history-card">
              <template #header>
                <div class="card-header">
                  <span>最近生成</span>
                  <el-button text type="primary" size="small" @click="loadHistory()">刷新</el-button>
                </div>
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
                <div class="card-header">
                  <span>生成结果</span>
                  <el-tag v-if="currentTask && currentTask.status === 'processing'" type="warning">
                    生成中...
                  </el-tag>
                </div>
              </template>

              <div v-if="currentTask && currentTask.status === 'processing'" class="generating-status">
                <el-progress type="circle" :percentage="currentTask.progress" />
                <p>正在生成图片，请稍候...</p>
              </div>

              <el-empty v-else-if="generatedImages.length === 0" description="请输入描述并点击生成图片" />
              
              <div v-else class="image-grid">
                <div v-for="(image, index) in generatedImages" :key="index" class="image-item">
                  <el-image
                    :src="image"
                    fit="contain"
                    :preview-src-list="generatedImages"
                    :initial-index="index"
                  />
                  <div class="image-actions">
                    <el-button size="small" type="primary" @click="downloadImage(image)">
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

      <aside class="side-panel">
        <div class="panel">
          <h3 class="panel-title">提示模板</h3>
          <p class="panel-subtitle">高质量描述能显著提升生成效果</p>
          <div class="info-list">
            <div class="info-item">
              <div class="info-icon"><el-icon><Star /></el-icon></div>
              <div>
                <div class="info-title">主体 + 场景</div>
                <div class="info-desc">例如：夜晚的城市街道，霓虹灯映照在雨后的地面。</div>
              </div>
            </div>
            <div class="info-item">
              <div class="info-icon"><el-icon><Star /></el-icon></div>
              <div>
                <div class="info-title">风格 + 光线</div>
                <div class="info-desc">补充写实、插画或电影感的光影描述。</div>
              </div>
            </div>
          </div>
        </div>

        <div class="panel">
          <h3 class="panel-title">参数提醒</h3>
          <div class="info-list">
            <div class="info-item">
              <div>
                <div class="info-title">AI模式</div>
                <div class="info-desc">{{ aiMode }}（{{ aiMode === 'Cookie' ? selectedPlatform : '消耗积分' }}）</div>
              </div>
            </div>
            <div class="info-item">
              <div>
                <div class="info-title">输出质量</div>
                <div class="info-desc">{{ form.quality }} / {{ form.size }}</div>
              </div>
            </div>
          </div>
        </div>
      </aside>
    </section>
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
  platform?: string
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
  platform: undefined,
})

// AI模式和平台选择
const aiMode = ref('API Key')
const selectedPlatform = ref('doubao')

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

  // Cookie模式需要选择平台
  if (aiMode.value === 'Cookie' && !selectedPlatform.value) {
    ElMessage.warning('请选择AI平台')
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
      platform: aiMode.value === 'Cookie' ? selectedPlatform.value : undefined,
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
        currentTask.value = null
        ElMessage.success('图片生成完成')
        loadHistory()
      } else if (task.status === 'failed') {
        stopPolling()
        currentTask.value = null
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
    historyList.value = result.items || []
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
  background: linear-gradient(180deg, #f8fbff 0%, #ffffff 40%);
  --hero-from: rgba(251, 191, 36, 0.18);
  --hero-to: rgba(245, 158, 11, 0.18);
  --page-accent: #d97706;

  :deep(.el-card) {
    border-radius: 14px;
    border: 1px solid #edf2f7;
    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.04);
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .input-card {
    margin-bottom: 20px;

    .model-card {
      margin-top: 20px;
    }
  }

  .history-card {
    margin-top: 20px;
  }

  .history-list {
    max-height: 300px;
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
        border-color: #f59e0b;
        background-color: #fffbeb;
      }

      &:last-child {
        margin-bottom: 0;
      }

      .history-thumbnail {
        width: 60px;
        height: 60px;
        border-radius: 8px;
        flex-shrink: 0;
      }

      .history-info {
        flex: 1;
        min-width: 0;

        .history-prompt {
          font-size: 13px;
          color: #303133;
          margin-bottom: 6px;
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

  .preview-card {
    min-height: 500px;

    .generating-status {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 60px 20px;

      p {
        margin-top: 20px;
        color: #606266;
      }
    }
  }

  .image-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
    gap: 16px;

    .image-item {
      border: 1px solid #e5e7eb;
      border-radius: 12px;
      overflow: hidden;
      background: #fff;
      box-shadow: 0 4px 12px rgba(15, 23, 42, 0.04);
      transition: all 0.3s;

      &:hover {
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08);
        transform: translateY(-2px);
      }

      .el-image {
        width: 100%;
        height: 240px;
      }

      .image-actions {
        padding: 12px;
        display: flex;
        gap: 8px;
        justify-content: center;
        background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
      }
    }
  }
}

@media (max-width: 992px) {
  .image-generation {
    .input-card {
      margin-bottom: 16px;
    }

    .history-card {
      margin-top: 16px;
    }
  }
}

@media (max-width: 768px) {
  .image-generation {
    .image-grid {
      grid-template-columns: 1fr;
    }
  }
}
</style>
