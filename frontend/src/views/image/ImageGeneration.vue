<template>
  <div class="image-generation">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>AI 图片生成（API Key）</span>
          <el-button type="primary" :loading="generating" @click="handleGenerate">生成</el-button>
        </div>
      </template>

      <el-form :model="form" label-position="top">
        <el-form-item label="提示词" required>
          <el-input v-model="form.prompt" type="textarea" :rows="5" maxlength="2000" show-word-limit />
        </el-form-item>
        <el-row :gutter="12">
          <el-col :span="8">
            <el-form-item label="宽度">
              <el-input-number v-model="form.width" :min="256" :max="2048" :step="64" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="高度">
              <el-input-number v-model="form.height" :min="256" :max="2048" :step="64" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="数量">
              <el-input-number v-model="form.num_images" :min="1" :max="4" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>

      <el-alert type="info" :closable="false" title="已移除 Cookie 授权生成模式，仅保留 API Key 模式" />
    </el-card>

    <el-card style="margin-top: 16px">
      <template #header><span>任务结果</span></template>
      <div v-if="taskId">
        <el-button size="small" @click="refreshTask" :loading="refreshing">刷新状态</el-button>
        <p>任务ID: {{ taskId }}</p>
        <p>状态: {{ taskStatus }}</p>
      </div>
      <el-row v-if="images.length" :gutter="12">
        <el-col v-for="img in images" :key="img" :span="8">
          <img :src="img" style="width: 100%; border-radius: 8px" />
        </el-col>
      </el-row>
      <el-empty v-else description="暂无图片" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/api/request'

const generating = ref(false)
const refreshing = ref(false)
const taskId = ref('')
const taskStatus = ref('')
const images = ref<string[]>([])

const form = reactive({
  prompt: '',
  width: 1024,
  height: 1024,
  num_images: 1,
})

const handleGenerate = async () => {
  if (!form.prompt.trim()) {
    ElMessage.warning('请输入提示词')
    return
  }

  generating.value = true
  try {
    const res = await request.post('/v1/image/generate', {
      prompt: form.prompt,
      width: form.width,
      height: form.height,
      num_images: form.num_images,
    })
    taskId.value = res.data.task_id
    taskStatus.value = res.data.status
    images.value = res.data.images || []
    ElMessage.success('任务已提交')
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '生成失败')
  } finally {
    generating.value = false
  }
}

const refreshTask = async () => {
  if (!taskId.value) return
  refreshing.value = true
  try {
    const res = await request.get(`/v1/image/task/${taskId.value}`)
    taskStatus.value = res.data.status
    images.value = res.data.images || []
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '刷新失败')
  } finally {
    refreshing.value = false
  }
}
</script>

<style scoped>
.image-generation { padding: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>
