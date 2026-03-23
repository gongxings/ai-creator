<template>
  <div class="ppt-editor-page">
    <div class="ppt-editor-header">
      <el-button @click="goBack" link>
        <el-icon><ArrowLeft /></el-icon>
        返回
      </el-button>
      <span class="title">{{ title }}</span>
      <div class="actions">
        <el-button @click="handleSave">保存</el-button>
        <el-button type="primary" @click="handleExport">导出PPTX</el-button>
      </div>
    </div>
    <div class="ppt-editor-container">
      <div v-if="loading" class="loading-overlay">
        <el-icon class="is-loading" :size="40"><Loading /></el-icon>
        <p>{{ loadingTip }}</p>
      </div>
      <iframe
        ref="iframeRef"
        :src="pptistUrl"
        frameborder="0"
        class="pptist-iframe"
        allow="fullscreen"
        allowfullscreen
        @load="onIframeLoad"
      ></iframe>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, Loading } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { savePPT } from '@/api/ppt'

const route = useRoute()
const router = useRouter()
const iframeRef = ref<HTMLIFrameElement>()
const title = ref('PPT编辑器')
const iframeReady = ref(false)
const loading = ref(false)
const loadingTip = ref('加载中...')
const currentPPTId = ref<number | null>(null)

// PPTist部署地址
// 开发环境：http://localhost:5173/
// 生产环境：/pptist/
const pptistUrl = computed(() => {
  const isDev = import.meta.env.DEV
  return isDev ? 'http://localhost:5173/?embed=true' : '/pptist/?embed=true'
})

const goBack = () => {
  router.back()
}

const loadAIPPTDataFromStorage = () => {
  try {
    const dataJson = localStorage.getItem('pptist_aippt_data')
    if (dataJson) {
      return JSON.parse(dataJson)
    }
  } catch (e) {
    console.error('Failed to load AIPPT data from localStorage:', e)
  }
  return null
}

const loadSlidesFromStorage = () => {
  try {
    const slidesJson = localStorage.getItem('pptist_slides')
    if (slidesJson) {
      return JSON.parse(slidesJson)
    }
  } catch (e) {
    console.error('Failed to load slides from localStorage:', e)
  }
  return null
}

const sendAIPPTToIframe = (data: any) => {
  if (iframeRef.value && iframeReady.value) {
    loading.value = true
    loadingTip.value = '正在生成PPT，请稍候...'
    iframeRef.value.contentWindow?.postMessage({
      type: 'LOAD_AIPPT',
      data: data
    }, '*')
  }
}

const sendSlidesToIframe = (slides: any) => {
  if (iframeRef.value && iframeReady.value) {
    iframeRef.value.contentWindow?.postMessage({
      type: 'LOAD_SLIDES',
      data: { slides }
    }, '*')
  }
}

const onIframeLoad = () => {
  console.log('PPTist iframe loaded')
}

const handleSave = () => {
  // 通过postMessage请求iframe保存数据
  iframeRef.value?.contentWindow?.postMessage({
    type: 'REQUEST_SAVE'
  }, '*')
}

const handleExport = () => {
  // 通过postMessage请求iframe导出PPTX
  iframeRef.value?.contentWindow?.postMessage({
    type: 'REQUEST_EXPORT'
  }, '*')
}

// 监听来自iframe的消息
const handleMessage = async (event: MessageEvent) => {
  const { type, data } = event.data || {}
  
  switch (type) {
    case 'READY':
      iframeReady.value = true
      // iframe准备就绪后，检查是否有AIPPT数据
      const aipptData = loadAIPPTDataFromStorage()
      if (aipptData) {
        // 发送AIPPT数据
        sendAIPPTToIframe(aipptData)
        // 清除数据，避免重复生成
        localStorage.removeItem('pptist_aippt_data')
      } else {
        // 没有AIPPT数据，加载已保存的幻灯片
        const slides = loadSlidesFromStorage()
        if (slides) {
          sendSlidesToIframe(slides)
        }
      }
      break
    case 'AIPPT_STARTED':
      loadingTip.value = '正在生成PPT，请稍候...'
      break
    case 'AIPPT_SUCCESS':
      loading.value = false
      ElMessage.success('PPT生成成功')
      break
    case 'SAVE_SUCCESS':
      // 保存到localStorage
      if (data?.slides) {
        localStorage.setItem('pptist_slides', JSON.stringify(data.slides))
        // 保存到数据库
        await saveToDatabase(data.slides)
      }
      break
    case 'EXPORT_SUCCESS':
      ElMessage.success('导出成功')
      break
    case 'TITLE_UPDATE':
      title.value = data?.title || 'PPT编辑器'
      break
    case 'ERROR':
      loading.value = false
      ElMessage.error(data?.message || '操作失败')
      break
  }
}

// 保存到数据库
const saveToDatabase = async (slides: any[]) => {
  try {
    // 弹出输入框让用户输入标题
    const { value: pptTitle } = await ElMessageBox.prompt('请输入PPT标题', '保存PPT', {
      confirmButtonText: '保存',
      cancelButtonText: '取消',
      inputPattern: /^.{1,200}$/,
      inputErrorMessage: '标题长度应在1-200字符之间',
      inputValue: title.value === 'PPT编辑器' ? '未命名PPT' : title.value,
    })
    
    if (!pptTitle) return
    
    // 获取模板ID
    const templateId = localStorage.getItem('pptist_template_id') || undefined
    
    // 保存到数据库
    const res = await savePPT({
      title: pptTitle,
      slides: slides,
      template_id: templateId,
    })
    
    currentPPTId.value = res.data.id
    title.value = pptTitle
    ElMessage.success('保存成功')
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('Save to database failed:', error)
      ElMessage.error('保存失败: ' + (error.message || '未知错误'))
    }
  }
}

onMounted(() => {
  window.addEventListener('message', handleMessage)
})

onUnmounted(() => {
  window.removeEventListener('message', handleMessage)
})
</script>

<style scoped lang="scss">
.ppt-editor-page {
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f5f5;
}

.ppt-editor-header {
  height: 56px;
  padding: 0 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
  z-index: 10;
  
  .title {
    font-size: 16px;
    font-weight: 500;
    color: #333;
  }
  
  .actions {
    display: flex;
    gap: 8px;
  }
}

.ppt-editor-container {
  flex: 1;
  overflow: hidden;
  position: relative;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 100;
  
  .el-icon {
    color: var(--el-color-primary);
    margin-bottom: 16px;
  }
  
  p {
    color: #606266;
    font-size: 14px;
  }
}

.pptist-iframe {
  width: 100%;
  height: 100%;
}
</style>
