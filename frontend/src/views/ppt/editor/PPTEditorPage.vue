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
import { useRouter, useRoute } from 'vue-router'
import { ArrowLeft, Loading } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { savePPT } from '@/api/ppt'
import { getPPTTemplateDetail } from '@/api/pptTemplate'

const router = useRouter()
const route = useRoute()
const iframeRef = ref<HTMLIFrameElement>()
const title = ref('PPT编辑器')
const iframeReady = ref(false)
const loading = ref(false)
const loadingTip = ref('加载中...')
const currentPPTId = ref<number | null>(null)
const pendingSlides = ref<any>(null) // 待发送的slides数据

// 从路由参数获取模板ID
const templateId = computed(() => {
  const id = route.params.id
  return id ? Number(id) : null
})

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

const sendTemplateToIframe = (template: any) => {
  if (iframeRef.value && iframeReady.value) {
    loading.value = true
    loadingTip.value = '正在加载模板...'
    // ppt_layout数据格式是 { slides, ... }，直接发送给iframe
    const slides = template.slides || template
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

// 根据ID加载模板
const loadTemplateById = async (id: number) => {
  loading.value = true
  loadingTip.value = '正在加载模板...'
  try {
    const res = await getPPTTemplateDetail(id)
    const template = res.data
    
    console.log('加载模板成功:', template.name, 'ppt_layout:', template.ppt_layout)
    
    // 更新标题
    title.value = template.name || 'PPT编辑器'
    
    // 将模板ID保存到localStorage，用于保存时使用
    localStorage.setItem('pptist_template_id', String(id))
    
    // PPT模板的布局数据在ppt_layout字段
    if (template.ppt_layout && template.ppt_layout.slides) {
      const slides = template.ppt_layout.slides
      
      // 如果iframe已ready，直接发送数据
      if (iframeReady.value) {
        sendSlidesToIframe(slides)
      } else {
        // 缓存数据，等iframe ready后发送
        pendingSlides.value = slides
      }
    } else {
      // 没有布局数据，关闭loading
      loading.value = false
      ElMessage.info('该模板暂无PPT布局数据')
    }
  } catch (error: any) {
    console.error('加载模板失败:', error)
    ElMessage.error(error.message || '加载模板失败')
    loading.value = false
  }
}

// 监听来自iframe的消息
const handleMessage = async (event: MessageEvent) => {
  const { type, data } = event.data || {}
  
  switch (type) {
    case 'READY':
      iframeReady.value = true
      // 如果有待发送的slides数据，发送给iframe
      if (pendingSlides.value) {
        sendSlidesToIframe(pendingSlides.value)
        pendingSlides.value = null
      } else if (templateId.value) {
        // 有模板ID但还没加载，开始加载
        loadTemplateById(templateId.value)
      } else {
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
      }
      break
    case 'AIPPT_STARTED':
      loadingTip.value = '正在生成PPT，请稍候...'
      break
    case 'AIPPT_SUCCESS':
    case 'SLIDES_LOADED':
      loading.value = false
      if (type === 'AIPPT_SUCCESS') {
        ElMessage.success('PPT生成成功')
      }
      break
    case 'SAVE_SUCCESS':
      // 保存到localStorage
      if (data?.slides) {
        localStorage.setItem('pptist_slides', JSON.stringify(data.slides))
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
