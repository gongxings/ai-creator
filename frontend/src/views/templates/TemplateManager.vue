<template>
  <div class="template-manager">
    <!-- 头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1>模板管理</h1>
        <p class="subtitle">管理文章排版模板，支持系统预设和自定义模板</p>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="handleCreate">
          <el-icon><Plus /></el-icon>
          创建模板
        </el-button>
      </div>
    </div>

    <!-- 主内容区 -->
    <div v-if="!showEditor" class="page-content">
      <!-- 筛选和搜索 -->
      <div class="filter-bar">
        <el-radio-group v-model="filterType" size="default">
          <el-radio-button value="all">全部</el-radio-button>
          <el-radio-button value="system">系统预设</el-radio-button>
          <el-radio-button value="custom">自定义</el-radio-button>
        </el-radio-group>
        <el-input
          v-model="searchKeyword"
          placeholder="搜索模板名称"
          prefix-icon="Search"
          style="width: 240px"
          clearable
        />
      </div>

      <!-- 模板列表 -->
      <div v-if="loading" class="loading-state">
        <el-skeleton :rows="5" animated />
      </div>

      <div v-else-if="filteredTemplates.length === 0" class="empty-state">
        <el-empty description="暂无模板">
          <el-button type="primary" @click="handleCreate">创建模板</el-button>
        </el-empty>
      </div>

      <div v-else class="template-grid">
        <div
          v-for="template in filteredTemplates"
          :key="template.id"
          class="template-card"
        >
          <!-- 预览区域 -->
          <div class="card-preview" @click="handlePreview(template)">
            <!-- PPT模板显示缩略图 -->
            <template v-if="template.platform === 'ppt' && template.thumbnail">
              <img 
                :src="template.thumbnail" 
                :alt="template.name"
                class="ppt-thumbnail"
              />
              <div class="preview-overlay">
                <el-icon><ZoomIn /></el-icon>
                <span>使用模板</span>
              </div>
            </template>
            <!-- 普通文章模板显示样式预览 -->
            <template v-else>
              <div 
                class="preview-content"
                :style="getPreviewStyle(template)"
              >
                <div class="preview-h1" :style="getElementStyle(template, 'h1')">示例标题</div>
                <div class="preview-p" :style="getElementStyle(template, 'p')">这是一段示例正文内容，用于展示模板的排版效果。</div>
                <div class="preview-quote" :style="getElementStyle(template, 'blockquote')">引用文字示例</div>
              </div>
              <div class="preview-overlay">
                <el-icon><ZoomIn /></el-icon>
                <span>查看预览</span>
              </div>
            </template>
          </div>

          <!-- 信息区域 -->
          <div class="card-info">
            <div class="info-header">
              <span class="name">{{ template.name }}</span>
              <div class="tags">
                <el-tag v-if="template.is_system" size="small" type="info">系统</el-tag>
                <el-tag v-else size="small" type="success">自定义</el-tag>
                <el-tag v-if="template.is_public && !template.is_system" size="small">公开</el-tag>
              </div>
            </div>
            <p v-if="template.description" class="description">{{ template.description }}</p>
            <div class="meta">
              <span><el-icon><Document /></el-icon> 使用 {{ template.use_count }} 次</span>
              <span><el-icon><Clock /></el-icon> {{ formatDate(template.created_at) }}</span>
            </div>
          </div>

          <!-- 操作区域 -->
          <div class="card-actions">
            <el-button-group>
              <el-tooltip :content="canEdit(template) ? '编辑' : '只能编辑自己创建的模板'" placement="top">
                <el-button 
                  :disabled="!canEdit(template)"
                  size="small"
                  @click="handleEdit(template)"
                >
                  <el-icon><Edit /></el-icon>
                </el-button>
              </el-tooltip>
              <el-tooltip content="克隆" placement="top">
                <el-button size="small" @click="handleClone(template)">
                  <el-icon><CopyDocument /></el-icon>
                </el-button>
              </el-tooltip>
              <el-tooltip :content="canDelete(template) ? '删除' : '只能删除自己创建的模板'" placement="top">
                <el-button 
                  :disabled="!canDelete(template)"
                  size="small"
                  type="danger"
                  @click="handleDelete(template)"
                >
                  <el-icon><Delete /></el-icon>
                </el-button>
              </el-tooltip>
            </el-button-group>
          </div>
        </div>
      </div>
    </div>

    <!-- 编辑器视图 -->
    <div v-else class="editor-view">
      <TemplateEditor
        :template="editingTemplate"
        @save="handleSaveTemplate"
        @cancel="handleCancelEdit"
      />
    </div>

    <!-- 预览对话框 -->
    <el-dialog
      v-model="previewDialogVisible"
      :title="previewTemplate?.name || '模板预览'"
      width="900px"
      destroy-on-close
    >
      <ContentPreview
        v-if="previewTemplate"
        :content="sampleMarkdown"
        :template="previewTemplate"
        :is-markdown="true"
        article-title="示例文章标题"
        style="height: 600px"
      />
    </el-dialog>

    <!-- 克隆对话框 -->
    <el-dialog
      v-model="cloneDialogVisible"
      title="克隆模板"
      width="400px"
    >
      <el-form :model="cloneForm" label-width="80px">
        <el-form-item label="新名称">
          <el-input v-model="cloneForm.name" placeholder="请输入新模板名称" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="cloneDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="cloning" @click="confirmClone">确认克隆</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Plus, 
  Edit, 
  Delete, 
  CopyDocument, 
  Document, 
  Clock,
  ZoomIn
} from '@element-plus/icons-vue'
import TemplateEditor from '@/components/TemplateEditor.vue'
import ContentPreview from '@/components/ContentPreview.vue'
import { sampleMarkdown } from '@/services/markdownRenderer'
import { getTemplates, deleteTemplate, cloneTemplate } from '@/api/templates'
import { useUserStore } from '@/store/user'
import type { ArticleTemplate, CSSProperties } from '@/types/template'

const router = useRouter()
const userStore = useUserStore()

const templates = ref<ArticleTemplate[]>([])
const loading = ref(false)
const filterType = ref('all')
const searchKeyword = ref('')

// 编辑器相关
const showEditor = ref(false)
const editingTemplate = ref<ArticleTemplate | null>(null)

// 预览对话框
const previewDialogVisible = ref(false)
const previewTemplate = ref<ArticleTemplate | null>(null)

// 克隆对话框
const cloneDialogVisible = ref(false)
const cloneForm = reactive({ name: '' })
const cloningTemplate = ref<ArticleTemplate | null>(null)
const cloning = ref(false)

// 过滤后的模板列表
const filteredTemplates = computed(() => {
  let result = templates.value

  // 按类型筛选
  if (filterType.value === 'system') {
    result = result.filter(t => t.is_system)
  } else if (filterType.value === 'custom') {
    result = result.filter(t => !t.is_system)
  }

  // 按关键词搜索
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(t => 
      t.name.toLowerCase().includes(keyword) ||
      t.description?.toLowerCase().includes(keyword)
    )
  }

  return result
})

// 加载模板列表
const loadTemplates = async () => {
  loading.value = true
  try {
    const res = await getTemplates({ limit: 100 })
    templates.value = res.items
  } catch (error: any) {
    console.error('加载模板失败:', error)
    ElMessage.error(error.message || '加载模板失败')
  } finally {
    loading.value = false
  }
}

// 判断模板是否属于当前用户
const isOwner = (template: ArticleTemplate): boolean => {
  // 系统模板不属于任何人
  if (template.is_system) return false
  // 如果没有user_id，认为是公共模板
  if (!template.user_id) return false
  // 判断是否是当前用户的模板
  const currentUserId = userStore.userInfo?.id
  return currentUserId !== undefined && template.user_id === currentUserId
}

// 判断是否可以编辑（只有自己的模板可以编辑）
const canEdit = (template: ArticleTemplate): boolean => {
  return isOwner(template)
}

// 判断是否可以删除（只有自己的模板可以删除）
const canDelete = (template: ArticleTemplate): boolean => {
  return isOwner(template)
}

// 创建模板
const handleCreate = () => {
  editingTemplate.value = null
  showEditor.value = true
}

// 编辑模板
const handleEdit = (template: ArticleTemplate) => {
  if (template.is_system) {
    ElMessage.warning('系统预设模板不能编辑，请克隆后修改')
    return
  }
  if (!isOwner(template)) {
    ElMessage.warning('只能编辑自己创建的模板')
    return
  }
  
  // PPT模板跳转到PPT编辑页面
  if (template.platform === 'ppt') {
    // 保存模板ID，编辑器会从API加载模板数据
    localStorage.setItem('pptist_template_id', String(template.id))
    localStorage.removeItem('pptist_slides') // 清除之前的slides
    router.push(`/ppt/editor/${template.id}`)
    return
  }
  
  editingTemplate.value = template
  showEditor.value = true
}

// 预览模板
const handlePreview = (template: ArticleTemplate) => {
  // PPT模板跳转到PPT生成页面
  if (template.platform === 'ppt') {
    router.push(`/ppt/editor/${template.id}`)
    return
  }
  
  previewTemplate.value = template
  previewDialogVisible.value = true
}

// 克隆模板
const handleClone = (template: ArticleTemplate) => {
  cloningTemplate.value = template
  cloneForm.name = `${template.name} (副本)`
  cloneDialogVisible.value = true
}

// 确认克隆
const confirmClone = async () => {
  if (!cloningTemplate.value) return
  
  if (!cloneForm.name.trim()) {
    ElMessage.warning('请输入新模板名称')
    return
  }

  cloning.value = true
  try {
    await cloneTemplate(cloningTemplate.value.id, cloneForm.name)
    ElMessage.success('模板克隆成功')
    cloneDialogVisible.value = false
    loadTemplates()
  } catch (error: any) {
    console.error('克隆模板失败:', error)
    ElMessage.error(error.message || '克隆失败')
  } finally {
    cloning.value = false
  }
}

// 删除模板
const handleDelete = async (template: ArticleTemplate) => {
  if (template.is_system) {
    ElMessage.warning('系统预设模板不能删除')
    return
  }
  if (!isOwner(template)) {
    ElMessage.warning('只能删除自己创建的模板')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定要删除模板"${template.name}"吗？此操作不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await deleteTemplate(template.id)
    ElMessage.success('模板已删除')
    loadTemplates()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除模板失败:', error)
      ElMessage.error(error.message || '删除失败')
    }
  }
}

// 保存模板
const handleSaveTemplate = () => {
  showEditor.value = false
  loadTemplates()
}

// 取消编辑
const handleCancelEdit = () => {
  showEditor.value = false
  editingTemplate.value = null
}

// 获取预览样式
const getPreviewStyle = (template: ArticleTemplate): Record<string, string> => {
  const container = template.styles?.container
  if (!container) return {}
  
  return {
    backgroundColor: container.backgroundColor || '#ffffff',
    fontFamily: container.fontFamily || 'inherit',
    padding: '12px'
  }
}

// 获取元素样式
const getElementStyle = (template: ArticleTemplate, element: string): Record<string, string> => {
  const styles = template.styles?.[element] as CSSProperties
  if (!styles) return {}
  
  const result: Record<string, string> = {}
  
  if (styles.color) result.color = styles.color
  if (styles.fontSize) result.fontSize = styles.fontSize
  if (styles.fontWeight) result.fontWeight = styles.fontWeight
  if (styles.borderLeft) result.borderLeft = styles.borderLeft
  if (styles.borderBottom) result.borderBottom = styles.borderBottom
  if (styles.backgroundColor) result.backgroundColor = styles.backgroundColor
  if (styles.paddingLeft) result.paddingLeft = styles.paddingLeft
  if (styles.padding) result.padding = styles.padding
  
  return result
}

// 格式化日期
const formatDate = (dateStr: string): string => {
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (days === 0) return '今天'
  if (days === 1) return '昨天'
  if (days < 7) return `${days}天前`
  if (days < 30) return `${Math.floor(days / 7)}周前`
  return date.toLocaleDateString('zh-CN')
}

onMounted(() => {
  loadTemplates()
})
</script>

<style scoped lang="scss">
.template-manager {
  min-height: 100%;
  padding: 24px;
  background: #f5f7fa;

  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 24px;

    h1 {
      font-size: 24px;
      font-weight: 600;
      color: #303133;
      margin: 0 0 8px 0;
    }

    .subtitle {
      font-size: 14px;
      color: #909399;
      margin: 0;
    }
  }

  .page-content {
    .filter-bar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
      padding: 16px 20px;
      background: #fff;
      border-radius: 8px;
    }

    .loading-state {
      padding: 40px;
      background: #fff;
      border-radius: 8px;
    }

    .empty-state {
      padding: 80px 40px;
      background: #fff;
      border-radius: 8px;
      text-align: center;
    }

    .template-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
      gap: 20px;
    }
  }

  .template-card {
    background: #fff;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
    transition: all 0.3s ease;

    &:hover {
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
      transform: translateY(-2px);

      .card-preview .preview-overlay {
        opacity: 1;
      }
    }

    .card-preview {
      position: relative;
      height: 180px;
      background: #f5f7fa;
      cursor: pointer;
      overflow: hidden;

      .ppt-thumbnail {
        width: 100%;
        height: 100%;
        object-fit: contain;
        padding: 8px;
      }

      .preview-content {
        height: 100%;
        overflow: hidden;

        .preview-h1 {
          font-size: 14px;
          font-weight: 600;
          margin-bottom: 8px;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }

        .preview-p {
          font-size: 12px;
          line-height: 1.6;
          margin-bottom: 8px;
          display: -webkit-box;
          -webkit-line-clamp: 3;
          -webkit-box-orient: vertical;
          overflow: hidden;
        }

        .preview-quote {
          font-size: 11px;
          padding: 6px 8px;
          border-radius: 4px;
          background: #f0f0f0;
        }
      }

      .preview-overlay {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        color: #fff;
        opacity: 0;
        transition: opacity 0.3s ease;

        .el-icon {
          font-size: 32px;
          margin-bottom: 8px;
        }

        span {
          font-size: 14px;
        }
      }
    }

    .card-info {
      padding: 16px;

      .info-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;

        .name {
          font-size: 16px;
          font-weight: 500;
          color: #303133;
        }

        .tags {
          display: flex;
          gap: 4px;
        }
      }

      .description {
        font-size: 13px;
        color: #909399;
        margin: 0 0 12px 0;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }

      .meta {
        display: flex;
        gap: 16px;
        font-size: 12px;
        color: #909399;

        span {
          display: flex;
          align-items: center;
          gap: 4px;
        }
      }
    }

    .card-actions {
      padding: 12px 16px;
      border-top: 1px solid #ebeef5;
      display: flex;
      justify-content: flex-end;
    }
  }

  .editor-view {
    background: #fff;
    border-radius: 8px;
    min-height: calc(100vh - 140px);
    overflow: hidden;
  }
}
</style>
