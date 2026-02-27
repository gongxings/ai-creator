<template>
  <div class="video-generation">
    <el-card class="header-card">
      <div class="header-content">
        <div>
          <h2>AI视频生成</h2>
          <p class="subtitle">仅支持 API Key 模式</p>
        </div>
      </div>
    </el-card>

    <el-row :gutter="16">
      <el-col :xs="24" :lg="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>生成参数</span>
              <el-button type="primary" :loading="generating" @click="generateVideo">生成视频</el-button>
            </div>
          </template>

          <el-tabs v-model="activeTab">
            <el-tab-pane label="文本生成视频" name="text">
              <el-form :model="textForm" label-position="top">
                <el-form-item label="视频描述" required>
                  <el-input v-model="textForm.prompt" type="textarea" :rows="6" maxlength="2000" show-word-limit />
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
                  <el-upload class="upload-area" drag :auto-upload="false" :on-change="handleImageChange" :limit="1" accept="image/*">
                    <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
                    <div class="el-upload__text">拖拽图片到此处或点击上传</div>
                  </el-upload>
                </el-form-item>
                <el-form-item label="运动描述">
                  <el-input v-model="imageForm.motion_prompt" type="textarea" :rows="3" maxlength="500" show-word-limit />
                </el-form-item>
              </el-form>
            </el-tab-pane>
          </el-tabs>

          <el-alert type="info" title="API Key 模式" :closable="false">
            <p>已移除 Cookie 授权模式，请在设置中配置可用模型 API Key。</p>
          </el-alert>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>任务状态</span>
            </div>
          </template>

          <div v-if="currentTask">
            <el-progress v-if="currentTask.status === 'processing'" :percentage="currentTask.progress" />
            <el-alert v-if="currentTask.status === 'failed'" type="error" :title="currentTask.error || '生成失败'" :closable="false" />
            <video v-if="currentTask.status === 'completed' && currentTask.video_url" :src="currentTask.video_url" controls class="video-element" />
          </div>
          <el-empty v-else description="暂无任务" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import type { UploadFile } from 'element-plus'
import request from '@/api/request'

interface TextForm { prompt: string; duration: number; aspect_ratio: string; style: string }
interface ImageForm { image: File | null; motion_prompt: string; duration: number; image_data_url?: string }
interface VideoTask { id: string; status: 'processing' | 'completed' | 'failed'; progress: number; video_url?: string; error?: string }

const activeTab = ref('text')
const generating = ref(false)
const currentTask = ref<VideoTask | null>(null)
let pollTimer: number | null = null

const textForm = reactive<TextForm>({ prompt: '', duration: 10, aspect_ratio: '16:9', style: 'realistic' })
const imageForm = reactive<ImageForm>({ image: null, motion_prompt: '', duration: 5 })

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

const generateVideo = async () => {
  if (activeTab.value === 'text' && !textForm.prompt.trim()) {
    ElMessage.warning('请输入视频描述')
    return
  }
  if (activeTab.value === 'image' && !imageForm.image) {
    ElMessage.warning('请上传图片')
    return
  }

  generating.value = true
  try {
    const response =
      activeTab.value === 'text'
        ? await request.post('/v1/video/text-to-video', {
            text: textForm.prompt,
            background_music: false,
            subtitle: true,
          })
        : await request.post('/v1/video/image-to-video', {
            images: imageForm.image_data_url ? [imageForm.image_data_url] : [],
            transition: 'fade',
            duration_per_image: imageForm.duration,
          })

    const task = response.data
    currentTask.value = { id: task.task_id, status: 'processing', progress: 0 }
    ElMessage.success('任务已提交')
    startPolling()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.message || '视频生成失败')
  } finally {
    generating.value = false
  }
}

const startPolling = () => {
  if (pollTimer) clearInterval(pollTimer)
  pollTimer = window.setInterval(async () => {
    if (!currentTask.value) return
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
      if (pollTimer) clearInterval(pollTimer)
      pollTimer = null
    }
  }, 3000)
}

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
})
</script>

<style scoped>
.video-generation { padding: 20px; }
.header-card { margin-bottom: 16px; }
.subtitle { margin: 4px 0 0; color: #909399; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.video-element { width: 100%; border-radius: 8px; }
</style>
