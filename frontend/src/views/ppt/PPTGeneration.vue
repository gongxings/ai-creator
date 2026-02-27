<template>
  <div class="ppt-generation">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>PPT 生成（API Key）</span>
          <el-button type="primary" :loading="generating" @click="handleGenerate">生成</el-button>
        </div>
      </template>

      <el-form :model="form" label-position="top">
        <el-form-item label="主题" required>
          <el-input v-model="form.topic" placeholder="输入PPT主题" />
        </el-form-item>
        <el-row :gutter="12">
          <el-col :span="8">
            <el-form-item label="页数">
              <el-input-number v-model="form.slides_count" :min="5" :max="30" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="风格">
              <el-input v-model="form.style" placeholder="business/modern..." />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="语言">
              <el-input v-model="form.language" placeholder="zh-CN" />
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
        <p v-if="pptUrl"><a :href="pptUrl" target="_blank">打开PPT</a></p>
      </div>
      <el-empty v-else description="暂无任务" />
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
const pptUrl = ref('')

const form = reactive({
  topic: '',
  slides_count: 10,
  style: 'business',
  language: 'zh-CN',
})

const handleGenerate = async () => {
  if (!form.topic.trim()) {
    ElMessage.warning('请输入主题')
    return
  }

  generating.value = true
  try {
    const res = await request.post('/v1/ppt/generate', {
      topic: form.topic,
      slides_count: form.slides_count,
      style: form.style,
      language: form.language,
    })
    taskId.value = res.data.task_id
    taskStatus.value = res.data.status
    pptUrl.value = res.data.ppt_url || ''
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
    const res = await request.get(`/v1/ppt/task/${taskId.value}`)
    taskStatus.value = res.data.status
    pptUrl.value = res.data.ppt_url || ''
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '刷新失败')
  } finally {
    refreshing.value = false
  }
}
</script>

<style scoped>
.ppt-generation { padding: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>
