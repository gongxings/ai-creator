<template>
  <div class="pptx-upload">
    <el-upload
      ref="uploadRef"
      class="upload-area"
      drag
      accept=".pptx"
      :auto-upload="false"
      :limit="1"
      :on-change="handleFileChange"
      :on-exceed="handleExceed"
    >
      <div class="upload-content">
        <el-icon class="upload-icon" :size="48"><Upload /></el-icon>
        <div class="upload-text">
          <p>将PPTX文件拖到此处，或<em>点击上传</em></p>
          <p class="upload-tip">只能上传.pptx文件</p>
        </div>
      </div>
    </el-upload>
    
    <div v-if="file" class="preview-section">
      <el-divider />
      <div class="preview-header">
        <h4>模板预览</h4>
        <el-button type="primary" :loading="uploading" @click="handleUpload">
          <el-icon><Upload /></el-icon>
          上传模板
        </el-button>
      </div>
      
      <div class="preview-content">
        <div class="preview-thumbnail">
          <img v-if="thumbnail" :src="thumbnail" alt="缩略图" />
          <div v-else class="thumbnail-placeholder">
            <el-icon :size="48"><Picture /></el-icon>
            <p>生成中...</p>
          </div>
        </div>
        
        <div class="preview-info">
          <el-form :model="formData" label-position="top">
            <el-form-item label="模板名称" required>
              <el-input v-model="formData.name" placeholder="请输入模板名称" />
            </el-form-item>
            <el-form-item label="模板描述">
              <el-input v-model="formData.description" type="textarea" :rows="3" placeholder="请输入模板描述（可选）" />
            </el-form-item>
          </el-form>
          
          <div v-if="jsonResult" class="json-info">
            <p>幻灯片数量: {{ jsonResult.slides?.length || 0 }}</p>
            <p>主题色: {{ jsonResult.themeColors?.join(', ') || '默认' }}</p>
            <p>尺寸: {{ jsonResult.size?.width || 960 }} × {{ jsonResult.size?.height || 540 }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage, UploadInstance, UploadProps } from 'element-plus'
import { Upload, Picture } from '@element-plus/icons-vue'
import { readFileAsArrayBuffer } from '@/utils/pptxConverter'
import { importPPTXTemplate } from '@/utils/pptxTemplateImport'
import { generateThumbnail } from '@/utils/thumbnailGenerator'
import { uploadPPTTemplate } from '@/api/pptTemplate'

const emit = defineEmits<{
  (e: 'success', template: { id: number; name: string; thumbnail?: string }): void
  (e: 'cancel'): void
}>()

const uploadRef = ref<UploadInstance>()
const file = ref<File | null>(null)
const thumbnail = ref<string>('')
const jsonResult = ref<any>(null)
const uploading = ref(false)

const formData = ref({
  name: '',
  description: '',
})

// 处理文件选择
const handleFileChange: UploadProps['onChange'] = async (uploadFile) => {
  if (!uploadFile.raw) return
  
  file.value = uploadFile.raw
  formData.value.name = uploadFile.name.replace('.pptx', '')
  
    try {
      // 解析PPTX
      const arrayBuffer = await readFileAsArrayBuffer(uploadFile.raw)
      const templateData = await importPPTXTemplate(arrayBuffer)
      
      console.log('=== PPTX转换结果 ===')
      console.log('幻灯片数量:', templateData.slides?.length)
      console.log('主题:', templateData.theme)
      
      const firstSlide = templateData.slides?.[0]
      if (firstSlide) {
        console.log('第一页背景:', firstSlide.background)
        console.log('第一页元素数量:', firstSlide.elements?.length)
      }
      
      jsonResult.value = templateData
      
      // 生成缩略图
      const thumbnailDataUrl = await generateThumbnail(templateData)
      thumbnail.value = thumbnailDataUrl
      
      ElMessage.success('PPTX解析成功')
  } catch (error: any) {
    console.error('解析失败:', error)
    ElMessage.error(error.message || 'PPTX解析失败')
  }
}

const handleExceed: UploadProps['onExceed'] = () => {
  ElMessage.warning('只能上传一个文件')
}

// 上传模板
const handleUpload = async () => {
  if (!file.value) {
    ElMessage.warning('请先选择文件')
    return
  }
  
  if (!formData.value.name.trim()) {
    ElMessage.warning('请输入模板名称')
    return
  }
  
  uploading.value = true
  
  try {
    const layoutJson = JSON.stringify(jsonResult.value)
    console.log('上传数据:', {
      name: formData.value.name,
      description: formData.value.description,
      pptx_file_size: file.value.size,
      thumbnail_size: thumbnail.value?.length || 0,
      layout_json_size: layoutJson.length,
    })
    
    // 将JSON转为文件上传
    const layoutBlob = new Blob([layoutJson], { type: 'application/json' })
    const layoutFile = new File([layoutBlob], 'layout.json', { type: 'application/json' })
    
    const res = await uploadPPTTemplate({
      name: formData.value.name,
      description: formData.value.description || undefined,
      pptx_file: file.value,
      thumbnail: thumbnail.value || undefined,
      layout_file: layoutFile,
    })
    
    ElMessage.success('模板上传成功')
    emit('success', res.data)
    
    // 重置状态
    resetState()
  } catch (error: any) {
    console.error('上传失败:', error)
    console.error('错误详情:', error.response?.data)
    ElMessage.error(error.response?.data?.detail || '上传失败')
  } finally {
    uploading.value = false
  }
}

// 重置状态
const resetState = () => {
  file.value = null
  thumbnail.value = ''
  jsonResult.value = null
  formData.value = { name: '', description: '' }
  uploadRef.value?.clearFiles()
}
</script>

<style scoped lang="scss">
.pptx-upload {
  padding: 16px;
}

.upload-area {
  width: 100%;
  
  :deep(.el-upload) {
    width: 100%;
  }
  
  :deep(.el-upload-dragger) {
    width: 100%;
  }
}

.upload-content {
  padding: 40px;
}

.upload-icon {
  color: var(--el-color-primary);
  margin-bottom: 16px;
}

.upload-text {
  em {
    color: var(--el-color-primary);
    font-style: normal;
  }
}

.upload-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 8px;
}

.preview-section {
  margin-top: 16px;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  
  h4 {
    margin: 0;
  }
}

.preview-content {
  display: flex;
  gap: 24px;
}

.preview-thumbnail {
  width: 320px;
  height: 180px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
  
  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
}

.thumbnail-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
  color: #909399;
  
  .el-icon {
    margin-bottom: 8px;
  }
}

.preview-info {
  flex: 1;
}

.json-info {
  margin-top: 16px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 8px;
  font-size: 14px;
  color: #606266;
  
  p {
    margin: 4px 0;
  }
}
</style>
