<template>
  <div class="ppt-generation">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>PPT 生成</span>
          <el-button type="primary" :loading="generating" @click="handleGenerate">生成</el-button>
        </div>
      </template>

      <el-form :model="form" label-position="top">
        <el-form-item label="选择模型" required>
          <el-select v-model="form.model_id" placeholder="请选择文本生成模型" style="width: 100%">
            <el-option
              v-for="model in textModels"
              :key="model.id"
              :label="`${model.name} (${model.provider})`"
              :value="model.id"
            />
          </el-select>
          <div v-if="!textModels.length" class="model-hint">
            暂无可用的文本生成模型，请先在 <router-link to="/settings">设置</router-link> 中添加支持文本生成的模型
          </div>
        </el-form-item>
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
              <el-select v-model="form.style" style="width: 100%">
                <el-option label="商务" value="business" />
                <el-option label="现代" value="modern" />
                <el-option label="简约" value="minimal" />
                <el-option label="创意" value="creative" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="语言">
              <el-select v-model="form.language" style="width: 100%">
                <el-option label="中文" value="zh-CN" />
                <el-option label="英文" value="en-US" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
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
import { reactive, ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/api/request'
import { getAIModels } from '@/api/models'
import type { AIModel } from '@/types'

const generating = ref(false)
const refreshing = ref(false)
const taskId = ref('')
const taskStatus = ref('')
const pptUrl = ref('')
const textModels = ref<AIModel[]>([])

const form = reactive({
  model_id: undefined as number | undefined,
  topic: '',
  slides_count: 10,
  style: 'business',
  language: 'zh-CN',
})

const loadTextModels = async () => {
  try {
    const res = await getAIModels('text')
    textModels.value = Array.isArray(res) ? res : (res as any).data || []
    // 默认选择第一个模型
    if (textModels.value.length && !form.model_id) {
      form.model_id = textModels.value[0].id
    }
  } catch {
    ElMessage.error('加载文本模型失败')
  }
}

const handleGenerate = async () => {
  if (!form.model_id) {
    ElMessage.warning('请选择模型')
    return
  }
  if (!form.topic.trim()) {
    ElMessage.warning('请输入主题')
    return
  }

  generating.value = true
  try {
    const res = await request.post('/v1/ppt/generate', {
      model_id: form.model_id,
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

onMounted(() => {
  loadTextModels()
})
</script>

<style scoped>
.ppt-generation { padding: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.model-hint { margin-top: 8px; color: #909399; font-size: 12px; }
.model-hint a { color: var(--el-color-primary); }
</style>
