<template>
  <div class="creation-history">
    <section class="page-hero">
      <div>
        <p class="eyebrow">Creation Archive</p>
        <h1>创作历史</h1>
        <p class="description">查看历史创作记录，按工具类型和时间快速筛选，并继续编辑已有内容。</p>
      </div>
    </section>

    <el-card class="glass-card filter-card">
      <template #header>
        <div class="panel-head"><div><h3>筛选条件</h3><p>按工具、时间和关键词快速定位历史内容。</p></div></div>
      </template>
      <el-form :inline="true" :model="filterForm" class="filter-form">
        <el-form-item label="工具类型">
          <el-select v-model="filterForm.toolType" placeholder="全部" clearable class="field-150">
            <el-option label="公众号文章" value="wechat_article" />
            <el-option label="小红书笔记" value="xiaohongshu_note" />
            <el-option label="公文写作" value="official_document" />
            <el-option label="营销文案" value="marketing_copy" />
          </el-select>
        </el-form-item>
        <el-form-item label="创建时间">
          <el-date-picker v-model="filterForm.dateRange" type="daterange" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" class="field-240" />
        </el-form-item>
        <el-form-item label="搜索">
          <el-input v-model="filterForm.keyword" placeholder="标题或内容关键词" clearable class="field-220">
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch"><el-icon><Search /></el-icon>搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="glass-card list-card">
      <template #header>
        <div class="panel-head panel-row"><div><h3>历史记录</h3><p>支持查看详情、继续编辑和删除记录。</p></div></div>
      </template>

      <div class="table-view">
        <el-table v-loading="loading" :data="creationList" style="width: 100%" @row-click="handleRowClick">
          <el-table-column prop="title" label="标题" min-width="220">
            <template #default="{ row }">
              <div class="title-cell">
                <el-icon :color="getToolColor(row.tool_type)"><component :is="getToolIcon(row.tool_type)" /></el-icon>
                <span>{{ row.title || '未命名内容' }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="tool_type" label="工具类型" width="140">
            <template #default="{ row }"><el-tag :type="getToolTagType(row.tool_type)" size="small" effect="plain">{{ getToolName(row.tool_type) }}</el-tag></template>
          </el-table-column>
          <el-table-column label="内容预览" min-width="300">
            <template #default="{ row }"><div class="content-preview">{{ getContentPreview(row.output_content || row.content) }}</div></template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" width="180">
            <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
          </el-table-column>
          <el-table-column label="操作" width="220" fixed="right">
            <template #default="{ row }">
              <el-button size="small" @click.stop="handleView(row)">查看</el-button>
              <el-button size="small" @click.stop="handleEdit(row)">编辑</el-button>
              <el-button size="small" type="danger" @click.stop="handleDelete(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <div class="card-view">
        <div v-for="row in creationList" :key="row.id" class="history-item">
          <div class="history-top">
            <div class="title-cell">
              <el-icon :color="getToolColor(row.tool_type)"><component :is="getToolIcon(row.tool_type)" /></el-icon>
              <span>{{ row.title || '未命名内容' }}</span>
            </div>
            <el-tag :type="getToolTagType(row.tool_type)" size="small" effect="plain">{{ getToolName(row.tool_type) }}</el-tag>
          </div>
          <div class="history-preview">{{ getContentPreview(row.output_content || row.content) }}</div>
          <div class="history-meta">{{ formatDate(row.created_at) }}</div>
          <div class="history-actions">
            <el-button size="small" @click="handleView(row)">查看</el-button>
            <el-button size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </div>
        </div>
      </div>

      <div class="pagination-container">
        <el-pagination v-model:current-page="pagination.page" v-model:page-size="pagination.pageSize" :total="pagination.total" :page-sizes="[10,20,50,100]" layout="total, sizes, prev, pager, next, jumper" @size-change="handleSizeChange" @current-change="handlePageChange" />
      </div>
    </el-card>

    <el-dialog v-model="showDetailDialog" :title="currentCreation?.title || '创作详情'" width="min(960px, 96vw)" destroy-on-close>
      <div v-if="currentCreation" class="detail-content">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="工具类型">{{ getToolName(currentCreation.tool_type) }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDate(currentCreation.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="更新时间">{{ formatDate(currentCreation.updated_at) }}</el-descriptions-item>
          <el-descriptions-item label="字数">{{ getWordCount(currentCreation.output_content || currentCreation.content) }}</el-descriptions-item>
        </el-descriptions>
        <el-divider />
        <div class="content-display" v-html="renderedContent"></div>
      </div>
      <template #footer>
        <el-button @click="showDetailDialog = false">关闭</el-button>
        <el-button type="primary" @click="handleCopyContent">复制内容</el-button>
        <el-button type="success" @click="handleEditFromDetail">继续编辑</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Document, Edit, Search } from '@element-plus/icons-vue'
import * as creationsApi from '@/api/creations'
import { markdownToHtml } from '@/services/markdownRenderer'
import dayjs from 'dayjs'

const router = useRouter()
const loading = ref(false)
const showDetailDialog = ref(false)
const creationList = ref<any[]>([])
const currentCreation = ref<any>(null)

const renderedContent = computed(() => {
  if (!currentCreation.value) return ''
  return markdownToHtml(currentCreation.value.output_content || currentCreation.value.content || '')
})

const filterForm = reactive({ toolType: '', dateRange: null as any, keyword: '' })
const pagination = reactive({ page: 1, pageSize: 20, total: 0 })

const toolNameMap: Record<string, string> = {
  wechat_article: '公众号', xiaohongshu_note: '小红书', official_document: '公文', marketing_copy: '营销', academic_paper: '论文', press_release: '新闻', video_script: '视频', story_novel: '故事', business_plan: '商业', work_report: '报告', resume: '简历', lesson_plan: '教案', content_rewrite: '改写', translation: '翻译'
}
const toolIconMap: Record<string, any> = { wechat_article: Document, xiaohongshu_note: Edit, official_document: Document, marketing_copy: Edit, academic_paper: Document, press_release: Document, video_script: Edit, story_novel: Edit, business_plan: Document, work_report: Document, resume: Document, lesson_plan: Document, content_rewrite: Edit, translation: Edit }
const toolColorMap: Record<string, string> = { wechat_article: '#07c160', xiaohongshu_note: '#ff2442', official_document: '#409eff', marketing_copy: '#f56c6c', academic_paper: '#909399', press_release: '#67c23a', video_script: '#e6a23c', story_novel: '#c71585', business_plan: '#1e90ff', work_report: '#409eff', resume: '#67c23a', lesson_plan: '#e6a23c', content_rewrite: '#909399', translation: '#409eff' }
const fetchCreations = async () => {
  loading.value = true
  try {
    const params: any = { page: pagination.page, page_size: pagination.pageSize }
    if (filterForm.toolType) params.tool_type = filterForm.toolType
    if (filterForm.keyword) params.keyword = filterForm.keyword
    if (filterForm.dateRange && filterForm.dateRange.length === 2) {
      params.start_date = dayjs(filterForm.dateRange[0]).format('YYYY-MM-DD')
      params.end_date = dayjs(filterForm.dateRange[1]).format('YYYY-MM-DD')
    }
    const response = await creationsApi.getCreations(params)
    creationList.value = response.items || []
    pagination.total = response.total || 0
  } catch (error: any) {
    ElMessage.error(error.message || '获取创作列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => { pagination.page = 1; fetchCreations() }
const handleReset = () => { filterForm.toolType = ''; filterForm.dateRange = null; filterForm.keyword = ''; pagination.page = 1; fetchCreations() }
const handlePageChange = (page: number) => { pagination.page = page; fetchCreations() }
const handleSizeChange = (size: number) => { pagination.pageSize = size; pagination.page = 1; fetchCreations() }
const handleRowClick = (row: any) => handleView(row)
const handleView = (row: any) => { currentCreation.value = row; showDetailDialog.value = true }
const handleEdit = (row: any) => { const toolType = row.tool_type || row.creation_type || 'wechat_article'; router.push({ name: 'WritingEditor', params: { toolType }, query: { id: row.id } }) }
const handleEditFromDetail = () => { if (currentCreation.value) { showDetailDialog.value = false; handleEdit(currentCreation.value) } }

const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm('确认删除这条创作记录吗？删除后无法恢复。', '确认删除', { confirmButtonText: '确认', cancelButtonText: '取消', type: 'warning' })
    await creationsApi.deleteCreation(row.id)
    ElMessage.success('删除成功')
    fetchCreations()
  } catch (error: any) {
    if (error !== 'cancel') ElMessage.error(error.message || '删除失败')
  }
}

const handleCopyContent = async () => {
  if (!currentCreation.value) return
  try {
    const text = (currentCreation.value.output_content || currentCreation.value.content || '').replace(/<[^>]+>/g, '')
    await navigator.clipboard.writeText(text)
    ElMessage.success('内容已复制到剪贴板')
  } catch {
    ElMessage.error('复制失败，请手动复制')
  }
}

const getToolName = (toolType: string) => toolNameMap[toolType] || toolType || '未知工具'
const getToolIcon = (toolType: string) => toolIconMap[toolType] || Document
const getToolColor = (toolType: string) => toolColorMap[toolType] || '#409eff'
const getToolTagType = (toolType: string) => ({ wechat_article: 'success', xiaohongshu_note: 'danger', official_document: 'primary', marketing_copy: 'warning', academic_paper: 'info', press_release: 'success', video_script: 'warning', story_novel: '', business_plan: 'primary', work_report: 'primary', resume: 'success', lesson_plan: 'warning', content_rewrite: 'info', translation: 'primary' }[toolType] || '')
const getContentPreview = (content: string) => (content || '').replace(/[#*`\[\]()_~>-]/g, '').replace(/\s+/g, ' ').trim().slice(0, 120)
const getWordCount = (content: string) => (content || '').replace(/[#*`\[\]()_~>-]/g, '').replace(/\s+/g, '').length
const formatDate = (value: string) => value ? dayjs(value).format('YYYY-MM-DD HH:mm') : '-'

onMounted(() => { fetchCreations() })
</script>

<style scoped lang="scss">
.creation-history{display:flex;flex-direction:column;gap:24px;padding:28px}.page-hero{padding:30px;border:1px solid rgba(148,163,184,.2);border-radius:30px;background:radial-gradient(circle at top right,rgba(125,211,252,.38),transparent 28%),linear-gradient(135deg,rgba(239,246,255,.94),rgba(255,255,255,.92));box-shadow:0 24px 60px rgba(15,23,42,.08)}.eyebrow{margin:0 0 10px;font-size:13px;font-weight:700;letter-spacing:.2em;text-transform:uppercase;color:#2563eb}.page-hero h1{margin:0;font-size:clamp(30px,4vw,42px);color:#12304a}.description{margin:14px 0 0;max-width:760px;font-size:15px;line-height:1.75;color:#60758e}.glass-card{border:1px solid rgba(148,163,184,.2);border-radius:26px;background:rgba(255,255,255,.9);box-shadow:0 20px 44px rgba(15,23,42,.07)}.panel-head{display:flex;justify-content:space-between;gap:16px}.panel-head h3{margin:0;font-size:20px;color:#12304a}.panel-head p{margin:8px 0 0;font-size:14px;color:#62748a}.filter-form :deep(.el-form-item){margin-bottom:12px}.field-150{width:150px}.field-220{width:220px}.field-240{width:240px}.title-cell{display:flex;align-items:center;gap:8px}.title-cell .el-icon{font-size:18px}.title-cell span{flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.content-preview,.history-preview{color:#60758e;line-height:1.7;display:-webkit-box;-webkit-box-orient:vertical;overflow:hidden;-webkit-line-clamp:2}.pagination-container{display:flex;justify-content:flex-end;margin-top:20px}.card-view{display:none}.history-item{padding:18px;border:1px solid rgba(148,163,184,.18);border-radius:20px;background:linear-gradient(180deg,rgba(248,250,252,.96),rgba(239,246,255,.82))}.history-top,.history-actions{display:flex;align-items:center;justify-content:space-between;gap:12px}.history-meta{margin-top:12px;font-size:13px;color:#66788a}.detail-content .content-display{margin-top:20px;padding:20px;background:linear-gradient(180deg,rgba(248,250,252,.96),rgba(239,246,255,.82));border-radius:18px;min-height:300px;max-height:520px;overflow:auto;line-height:1.8}.detail-content .content-display :deep(blockquote){margin:12px 0;padding:10px 16px;border-left:4px solid #3b82f6;background:rgba(239,246,255,.9)}.detail-content .content-display :deep(pre){padding:14px;border-radius:14px;background:#0f172a;color:#e2e8f0;overflow:auto}.detail-content .content-display :deep(img){max-width:100%;height:auto;border-radius:12px}@media (max-width:768px){.creation-history{padding:16px}.filter-form{display:block}.field-150,.field-220,.field-240{width:100%}.table-view{display:none}.card-view{display:flex;flex-direction:column;gap:14px}.pagination-container{justify-content:center}.history-top,.history-actions,.panel-head{flex-direction:column;align-items:flex-start}}
</style>
