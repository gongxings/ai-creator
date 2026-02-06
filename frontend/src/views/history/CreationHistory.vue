<template>
  <div class="creation-history flagship-page page-shell">
    <section class="page-hero history-hero">
      <div class="hero-grid">
        <div class="hero-main">
          <span class="hero-eyebrow">History</span>
          <h1 class="hero-title">创作历史</h1>
          <p class="hero-subtitle">追踪你的内容创作与发布进度，随时回看与复用。</p>
          <div class="hero-actions">
            <el-button type="primary" @click="handleSearch">刷新筛选</el-button>
            <el-button @click="handleReset">重置条件</el-button>
          </div>
        </div>
        <div class="hero-panel">
          <div class="hero-panel-title">历史概览</div>
          <div class="hero-stats">
            <div class="hero-stat">
              <div class="hero-stat-value">{{ pagination.total }}</div>
              <div class="hero-stat-label">累计记录</div>
            </div>
            <div class="hero-stat">
              <div class="hero-stat-value">{{ creationList.length }}</div>
              <div class="hero-stat-label">当前列表</div>
            </div>
            <div class="hero-stat">
              <div class="hero-stat-value">{{ filterForm.toolType || '全部' }}</div>
              <div class="hero-stat-label">筛选类型</div>
            </div>
            <div class="hero-stat">
              <div class="hero-stat-value">{{ filterForm.keyword ? '已筛选' : '未筛选' }}</div>
              <div class="hero-stat-label">关键词</div>
            </div>
          </div>
          <div class="hero-tags">
            <span class="hero-tag">可编辑</span>
            <span class="hero-tag">可复制</span>
            <span class="hero-tag">多平台发布</span>
          </div>
        </div>
      </div>
    </section>

    <section class="page-dashboard">
      <div class="dashboard-grid">
        <div class="dashboard-card">
          <div class="label">累计记录</div>
          <div class="value">{{ pagination.total }}</div>
          <div class="delta">内容沉淀可追溯</div>
        </div>
        <div class="dashboard-card">
          <div class="label">当前页数</div>
          <div class="value">{{ pagination.page }}</div>
          <div class="delta">支持多条件筛选</div>
        </div>
        <div class="dashboard-card">
          <div class="label">筛选状态</div>
          <div class="value">{{ filterForm.keyword ? '已筛选' : '全部' }}</div>
          <div class="delta">快速定位目标内容</div>
        </div>
      </div>
    </section>

    <section class="page-body">
      <div class="main-panel">
        <div class="history-container">
      <!-- 筛选栏 -->
      <el-card class="filter-card">
        <el-form :inline="true" :model="filterForm">
          <el-form-item label="工具类型">
            <el-select v-model="filterForm.toolType" placeholder="全部" clearable style="width: 150px">
              <el-option label="公众号文章" value="wechat_article" />
              <el-option label="小红书笔记" value="xiaohongshu_note" />
              <el-option label="公文写作" value="official_document" />
              <el-option label="营销文案" value="marketing_copy" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="创建时间">
            <el-date-picker
              v-model="filterForm.dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              style="width: 240px"
            />
          </el-form-item>

          <el-form-item label="搜索">
            <el-input
              v-model="filterForm.keyword"
              placeholder="标题或内容"
              clearable
              style="width: 200px"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="handleSearch">
              <el-icon><Search /></el-icon>
              搜索
            </el-button>
            <el-button @click="handleReset">重置</el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <!-- 列表 -->
      <el-card class="list-card">
        <el-table
          v-loading="loading"
          :data="creationList"
          style="width: 100%"
          @row-click="handleRowClick"
        >
          <el-table-column prop="title" label="标题" min-width="200">
            <template #default="{ row }">
              <div class="title-cell">
                <el-icon :color="getToolColor(row.tool_type)">
                  <component :is="getToolIcon(row.tool_type)" />
                </el-icon>
                <span>{{ row.title }}</span>
              </div>
            </template>
          </el-table-column>

          <el-table-column prop="tool_type" label="工具类型" width="120">
            <template #default="{ row }">
              <el-tag :type="getToolTagType(row.tool_type)" size="small">
                {{ getToolName(row.tool_type) }}
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column prop="content" label="内容预览" min-width="300">
            <template #default="{ row }">
              <div class="content-preview">
                {{ getContentPreview(row.content) }}
              </div>
            </template>
          </el-table-column>

          <el-table-column prop="created_at" label="创建时间" width="180">
            <template #default="{ row }">
              {{ formatDate(row.created_at) }}
            </template>
          </el-table-column>

          <el-table-column label="操作" width="200" fixed="right">
            <template #default="{ row }">
              <el-button size="small" @click.stop="handleView(row)">
                查看
              </el-button>
              <el-button size="small" @click.stop="handleEdit(row)">
                编辑
              </el-button>
              <el-button
                size="small"
                type="danger"
                @click.stop="handleDelete(row)"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <div class="pagination-container">
          <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.pageSize"
            :total="pagination.total"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handlePageChange"
          />
        </div>
      </el-card>
        </div>
      </div>
      <aside class="side-panel">
        <div class="panel">
          <h3 class="panel-title">历史使用指南</h3>
          <p class="panel-subtitle">支持查看、编辑与复制内容</p>
          <div class="info-list">
            <div class="info-item">
              <div class="info-icon"><el-icon><Document /></el-icon></div>
              <div>
                <div class="info-title">快速筛选</div>
                <div class="info-desc">按时间或关键词定位目标内容。</div>
              </div>
            </div>
            <div class="info-item">
              <div class="info-icon"><el-icon><Edit /></el-icon></div>
              <div>
                <div class="info-title">再次编辑</div>
                <div class="info-desc">点击编辑继续优化内容质量。</div>
              </div>
            </div>
            <div class="info-item">
              <div class="info-icon"><el-icon><Search /></el-icon></div>
              <div>
                <div class="info-title">复用内容</div>
                <div class="info-desc">复制并快速生成新版本。</div>
              </div>
            </div>
          </div>
        </div>
        <div class="panel">
          <h3 class="panel-title">筛选状态</h3>
          <div class="info-list">
            <div class="info-item">
              <div>
                <div class="info-title">工具类型</div>
                <div class="info-desc">{{ filterForm.toolType || '全部' }}</div>
              </div>
            </div>
            <div class="info-item">
              <div>
                <div class="info-title">关键词</div>
                <div class="info-desc">{{ filterForm.keyword || '未填写' }}</div>
              </div>
            </div>
          </div>
        </div>
      </aside>
    </section>

    <!-- 查看详情对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      :title="currentCreation?.title"
      width="800px"
      destroy-on-close
    >
      <div v-if="currentCreation" class="detail-content">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="工具类型">
            {{ getToolName(currentCreation.tool_type) }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatDate(currentCreation.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="更新时间">
            {{ formatDate(currentCreation.updated_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="字数">
            {{ getWordCount(currentCreation.content) }}
          </el-descriptions-item>
        </el-descriptions>

        <el-divider />

        <div class="content-display" v-html="currentCreation.content"></div>
      </div>

      <template #footer>
        <el-button @click="showDetailDialog = false">关闭</el-button>
        <el-button type="primary" @click="handleCopyContent">
          复制内容
        </el-button>
        <el-button type="success" @click="handleEditFromDetail">
          编辑
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Document, Edit } from '@element-plus/icons-vue'
import * as creationsApi from '@/api/creations'
import dayjs from 'dayjs'

const router = useRouter()

const loading = ref(false)
const showDetailDialog = ref(false)
const creationList = ref<any[]>([])
const currentCreation = ref<any>(null)

const filterForm = reactive({
  toolType: '',
  dateRange: null as any,
  keyword: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

// 工具配置映射
const toolNameMap: Record<string, string> = {
  wechat_article: '公众号',
  xiaohongshu_note: '小红书',
  official_document: '公文',
  marketing_copy: '营销',
  academic_paper: '论文',
  press_release: '新闻',
  video_script: '视频',
  story_novel: '故事',
  business_plan: '商业',
  work_report: '报告',
  resume: '简历',
  lesson_plan: '教案',
  content_rewrite: '改写',
  translation: '翻译'
}

const toolIconMap: Record<string, any> = {
  wechat_article: Document,
  xiaohongshu_note: Edit,
  official_document: Document,
  marketing_copy: Edit,
  academic_paper: Document,
  press_release: Document,
  video_script: Edit,
  story_novel: Edit,
  business_plan: Document,
  work_report: Document,
  resume: Document,
  lesson_plan: Document,
  content_rewrite: Edit,
  translation: Edit
}

const toolColorMap: Record<string, string> = {
  wechat_article: '#07c160',
  xiaohongshu_note: '#ff2442',
  official_document: '#409eff',
  marketing_copy: '#f56c6c',
  academic_paper: '#909399',
  press_release: '#67c23a',
  video_script: '#e6a23c',
  story_novel: '#c71585',
  business_plan: '#1e90ff',
  work_report: '#409eff',
  resume: '#67c23a',
  lesson_plan: '#e6a23c',
  content_rewrite: '#909399',
  translation: '#409eff'
}

// 获取创作列表
const fetchCreations = async () => {
  loading.value = true
  try {
    const params: any = {
      page: pagination.page,
      page_size: pagination.pageSize
    }

    if (filterForm.toolType) {
      params.tool_type = filterForm.toolType
    }

    if (filterForm.keyword) {
      params.keyword = filterForm.keyword
    }

    if (filterForm.dateRange && filterForm.dateRange.length === 2) {
      params.start_date = dayjs(filterForm.dateRange[0]).format('YYYY-MM-DD')
      params.end_date = dayjs(filterForm.dateRange[1]).format('YYYY-MM-DD')
    }

    const response = await creationsApi.getCreations(params)
    creationList.value = response.items
    pagination.total = response.total
  } catch (error: any) {
    ElMessage.error(error.message || '获取创作列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  fetchCreations()
}

// 重置
const handleReset = () => {
  filterForm.toolType = ''
  filterForm.dateRange = null
  filterForm.keyword = ''
  pagination.page = 1
  fetchCreations()
}

// 分页变化
const handlePageChange = (page: number) => {
  pagination.page = page
  fetchCreations()
}

const handleSizeChange = (size: number) => {
  pagination.pageSize = size
  pagination.page = 1
  fetchCreations()
}

// 行点击
const handleRowClick = (row: any) => {
  handleView(row)
}

// 查看详情
const handleView = (row: any) => {
  currentCreation.value = row
  showDetailDialog.value = true
}

// 编辑
const handleEdit = (row: any) => {
  router.push({
    name: 'WritingEditor',
    query: {
      id: row.id,
      tool_type: row.tool_type
    }
  })
}

// 从详情编辑
const handleEditFromDetail = () => {
  if (currentCreation.value) {
    showDetailDialog.value = false
    handleEdit(currentCreation.value)
  }
}

// 删除
const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这条创作记录吗？删除后无法恢复。',
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await creationsApi.deleteCreation(row.id)
    ElMessage.success('删除成功')
    fetchCreations()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

// 复制内容
const handleCopyContent = async () => {
  if (!currentCreation.value) return

  try {
    // 创建临时元素来提取纯文本
    const tempDiv = document.createElement('div')
    tempDiv.innerHTML = currentCreation.value.content
    const text = tempDiv.textContent || tempDiv.innerText || ''

    await navigator.clipboard.writeText(text)
    ElMessage.success('内容已复制到剪贴板')
  } catch (error) {
    ElMessage.error('复制失败，请手动复制')
  }
}

// 工具辅助函数
const getToolName = (toolType: string) => {
  return toolNameMap[toolType] || toolType
}

const getToolIcon = (toolType: string) => {
  return toolIconMap[toolType] || Document
}

const getToolColor = (toolType: string) => {
  return toolColorMap[toolType] || '#409eff'
}

const getToolTagType = (toolType: string) => {
  const typeMap: Record<string, any> = {
    wechat_article: 'success',
    xiaohongshu_note: 'danger',
    official_document: 'primary',
    marketing_copy: 'warning',
    academic_paper: 'info',
    press_release: 'success',
    video_script: 'warning',
    story_novel: '',
    business_plan: 'primary',
    work_report: 'primary',
    resume: 'success',
    lesson_plan: 'warning',
    content_rewrite: 'info',
    translation: 'primary'
  }
  return typeMap[toolType] || ''
}

const getContentPreview = (content: string) => {
  if (!content) return ''
  // 移除HTML标签
  const text = content.replace(/<[^>]*>/g, '')
  // 截取前100个字符
  return text.length > 100 ? text.substring(0, 100) + '...' : text
}

const formatDate = (date: string) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm:ss')
}

const getWordCount = (content: string) => {
  if (!content) return 0
  // 移除HTML标签
  const text = content.replace(/<[^>]*>/g, '')
  // 计算字数（中文按字符，英文按单词）
  const chineseCount = (text.match(/[\u4e00-\u9fa5]/g) || []).length
  const englishCount = (text.match(/[a-zA-Z]+/g) || []).length
  return chineseCount + englishCount
}

// 组件挂载时获取数据
onMounted(() => {
  fetchCreations()
})
</script>

<style scoped lang="scss">
.creation-history {
  padding: 20px;
  --hero-from: rgba(99, 102, 241, 0.18);
  --hero-to: rgba(59, 130, 246, 0.18);
  --page-accent: #4f46e5;

  .history-container {
    margin-top: 20px;

    .filter-card {
      margin-bottom: 20px;
    }

    .list-card {
      .title-cell {
        display: flex;
        align-items: center;
        gap: 8px;

        .el-icon {
          font-size: 18px;
        }

        span {
          flex: 1;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }
      }

      .content-preview {
        color: #606266;
        line-height: 1.5;
        overflow: hidden;
        text-overflow: ellipsis;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
      }

      .pagination-container {
        margin-top: 20px;
        display: flex;
        justify-content: flex-end;
      }
    }
  }

  .detail-content {
    .content-display {
      margin-top: 20px;
      padding: 20px;
      background-color: #f5f7fa;
      border-radius: 4px;
      min-height: 300px;
      max-height: 500px;
      overflow-y: auto;
      line-height: 1.8;

      :deep(h1),
      :deep(h2),
      :deep(h3),
      :deep(h4),
      :deep(h5),
      :deep(h6) {
        margin: 16px 0 8px;
        font-weight: 600;
      }

      :deep(p) {
        margin: 8px 0;
      }

      :deep(ul),
      :deep(ol) {
        margin: 8px 0;
        padding-left: 24px;
      }

      :deep(li) {
        margin: 4px 0;
      }

      :deep(blockquote) {
        margin: 8px 0;
        padding: 8px 16px;
        border-left: 4px solid #409eff;
        background-color: #ecf5ff;
      }

      :deep(code) {
        padding: 2px 4px;
        background-color: #f4f4f5;
        border-radius: 2px;
        font-family: 'Courier New', monospace;
      }

      :deep(pre) {
        margin: 8px 0;
        padding: 12px;
        background-color: #282c34;
        color: #abb2bf;
        border-radius: 4px;
        overflow-x: auto;

        code {
          background-color: transparent;
          color: inherit;
        }
      }
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .creation-history {
    padding: 10px;

    .history-container {
      .filter-card {
        :deep(.el-form) {
          .el-form-item {
            display: block;
            margin-right: 0;
            margin-bottom: 12px;

            .el-select,
            .el-date-picker,
            .el-input {
              width: 100% !important;
            }
          }
        }
      }

      .list-card {
        :deep(.el-table) {
          font-size: 12px;

          .el-button {
            padding: 5px 8px;
            font-size: 12px;
          }
        }

        .pagination-container {
          :deep(.el-pagination) {
            justify-content: center;

            .el-pagination__sizes,
            .el-pagination__jump {
              display: none;
            }
          }
        }
      }
    }

    .detail-content {
      .content-display {
        padding: 12px;
        font-size: 14px;
      }
    }
  }
}
</style>

