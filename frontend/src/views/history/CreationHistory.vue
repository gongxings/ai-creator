<template>
  <div class="creation-history">
    <el-page-header content="创作历史" />

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
import { creationsApi } from '@/api/creations'
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
  resume:
