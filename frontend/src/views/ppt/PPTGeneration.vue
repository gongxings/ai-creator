<template>
  <div class="ppt-generation">
    <el-card class="header-card">
      <h2>AI PPT生成</h2>
      <p class="subtitle">使用AI技术，快速生成专业PPT演示文稿</p>
    </el-card>

    <el-row :gutter="20">
      <el-col :xs="24" :lg="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>PPT生成</span>
              <el-button type="primary" :loading="generating" @click="generatePPT">
                <el-icon><Document /></el-icon>
                生成PPT
              </el-button>
            </div>
          </template>

          <el-tabs v-model="activeTab">
            <el-tab-pane label="主题生成" name="theme">
              <el-form :model="themeForm" label-position="top">
                <el-form-item label="PPT主题" required>
                  <el-input
                    v-model="themeForm.theme"
                    placeholder="例如：人工智能在教育领域的应用"
                    maxlength="100"
                    show-word-limit
                  />
                </el-form-item>
                <el-form-item label="页数">
                  <el-slider v-model="themeForm.pages" :min="5" :max="30" :marks="{ 5: '5', 15: '15', 30: '30' }" />
                </el-form-item>
                <el-form-item label="风格">
                  <el-select v-model="themeForm.style">
                    <el-option label="商务" value="business" />
                    <el-option label="简约" value="simple" />
                    <el-option label="创意" value="creative" />
                  </el-select>
                </el-form-item>
              </el-form>
            </el-tab-pane>

            <el-tab-pane label="大纲生成" name="outline">
              <el-form :model="outlineForm" label-position="top">
                <el-form-item label="PPT大纲" required>
                  <el-input
                    v-model="outlineForm.outline"
                    type="textarea"
                    :rows="12"
                    placeholder="请输入PPT大纲，每行一个要点"
                    maxlength="2000"
                    show-word-limit
                  />
                </el-form-item>
              </el-form>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="12">
        <el-card>
          <template #header>
            <span>生成结果</span>
          </template>
          <el-empty v-if="!currentPPT" description="请输入内容并点击生成PPT" />
          <div v-else class="ppt-preview">
            <el-alert v-if="currentPPT.status === 'processing'" title="PPT生成中..." type="warning" :closable="false">
              <el-progress :percentage="currentPPT.progress" />
            </el-alert>
            <div v-else-if="currentPPT.status === 'completed'">
              <div class="ppt-info">
                <p>PPT已生成完成</p>
              </div>
              <div class="ppt-actions">
                <el-button type="primary" @click="downloadPPT">
                  <el-icon><Download /></el-icon>
                  下载PPT
                </el-button>
                <el-button @click="previewPPT">
                  <el-icon><View /></el-icon>
                  在线预览
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
import { ref, reactive, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Document, Download, View } from '@element-plus/icons-vue'
import request from '@/api/request'

const activeTab = ref('theme')
const generating = ref(false)
const currentPPT = ref<any>(null)

const themeForm = reactive({
  theme: '',
  pages: 10,
  style: 'business',
})

const outlineForm = reactive({
  outline: '',
})

const currentTaskId = ref<string | null>(null)
let pollTimer: number | null = null

const generatePPT = async () => {
  if (activeTab.value === 'theme' && !themeForm.theme.trim()) {
    ElMessage.warning('请输入PPT主题')
    return
  }
  if (activeTab.value === 'outline' && !outlineForm.outline.trim()) {
    ElMessage.warning('请输入PPT大纲')
    return
  }

  generating.value = true
  try {
    let result
    if (activeTab.value === 'theme') {
      result = await request.post('/v1/ppt/generate', {
        topic: themeForm.theme,
        slides_count: themeForm.pages,
        style: themeForm.style,
      })
    } else {
      result = await request.post('/v1/ppt/from-outline', {
        outline: outlineForm.outline,
      })
    }
    const task = result.data
    currentTaskId.value = task.task_id
    currentPPT.value = null
    ElMessage.success('PPT生成任务已提交')
    startPolling()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.message || 'PPT生成失败')
  } finally {
    generating.value = false
  }
}

const downloadPPT = () => {
  if (currentPPT.value?.ppt_url) {
    window.open(currentPPT.value.ppt_url)
  }
}

const previewPPT = () => {
  if (currentPPT.value?.ppt_url) {
    window.open(currentPPT.value.ppt_url, '_blank')
    return
  }
  ElMessage.warning('暂无可预览的PPT文件')
}

const startPolling = () => {
  if (!currentTaskId.value) return
  if (pollTimer) {
    clearInterval(pollTimer)
  }
  pollTimer = window.setInterval(async () => {
    if (!currentTaskId.value) return
    try {
      const result = await request.get(`/v1/ppt/task/${currentTaskId.value}`)
      const task = result.data
      if (task.status === 'completed') {
        currentPPT.value = task
        stopPolling()
        ElMessage.success('PPT生成完成')
      } else if (task.status === 'failed') {
        stopPolling()
        ElMessage.error('PPT生成失败')
      }
    } catch (error) {
      console.error('获取PPT任务状态失败', error)
    }
  }, 3000)
}

const stopPolling = () => {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

onUnmounted(() => {
  stopPolling()
})
</script>

<style scoped lang="scss">
.ppt-generation {
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

  :deep(.el-tabs__item.is-active) {
    color: #2563eb;
    font-weight: 600;
  }

  :deep(.el-tabs__active-bar) {
    background-color: #2563eb;
  }

  .ppt-preview {
    min-height: 300px;
    padding-top: 12px;

    .ppt-info {
      text-align: center;
      padding: 20px;
      font-size: 16px;
      color: #606266;
    }

    .ppt-actions {
      display: flex;
      gap: 12px;
      justify-content: center;
      margin-top: 20px;
    }
  }
}

@media (max-width: 768px) {
  .ppt-generation {
    padding: 12px;
  }
}
</style>
