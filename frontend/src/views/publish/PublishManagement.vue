<template>
  <div class="publish-management flagship-page page-shell">
    <section class="page-hero publish-hero">
      <el-card class="header-card">
      <div class="header-content">
        <div class="header-left">
          <h2>发布管理</h2>
          <p class="subtitle">一键发布到多个平台</p>
        </div>
        <el-button type="primary" @click="showPublishDialog = true">
          <el-icon><Upload /></el-icon>
          新建发布
        </el-button>
      </div>
      </el-card>
    </section>

    <section class="page-dashboard">
      <div class="dashboard-grid">
        <div class="dashboard-card">
          <div class="label">发布历史</div>
          <div class="value">{{ publishHistory.length }}</div>
          <div class="delta">内容沉淀可追溯</div>
        </div>
        <div class="dashboard-card">
          <div class="label">发布状态</div>
          <div class="value">{{ publishing ? '发布中' : '就绪' }}</div>
          <div class="delta">支持定时与立即发布</div>
        </div>
        <div class="dashboard-card">
          <div class="label">发布成功率</div>
          <div class="value">{{ successRate }}%</div>
          <div class="delta">持续优化中</div>
        </div>
      </div>
    </section>

    <section class="page-body">
      <div class="main-panel">
    <!-- 提示：去账号授权页面 -->
    <el-alert
      v-if="platformAccounts.length === 0"
      title="还没有绑定发布平台账号"
      type="warning"
      :closable="false"
      style="margin-bottom: 20px"
    >
      <template #default>
        <p>请先前往账号授权页面绑定发布平台账号（如微信公众号、小红书等），然后再进行发布操作。</p>
        <el-button type="primary" size="small" @click="router.push('/authorization')">
          <el-icon><Key /></el-icon>
          前往账号授权
        </el-button>
      </template>
    </el-alert>

    <!-- 发布历史 -->
    <el-card class="history-card">
      <template #header>
        <div class="card-header">
          <span>发布历史</span>
          <el-input
            v-model="searchKeyword"
            placeholder="搜索标题"
            class="search-input"
            clearable
            @input="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </div>
      </template>

      <!-- 桌面版表格 -->
      <div class="table-view">
        <el-table :data="publishHistory" v-loading="loading">
          <el-table-column prop="title" label="标题" min-width="200" />
          <el-table-column prop="platform" label="发布平台" width="200">
            <template #default="{ row }">
              <el-tag size="small">
                {{ getPlatformName(row.platform) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="120">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)">
                {{ getStatusText(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="发布时间" width="180">
            <template #default="{ row }">
              {{
                row.status === 'scheduled' && row.scheduled_at
                  ? formatDate(row.scheduled_at)
                  : row.published_at
                  ? formatDate(row.published_at)
                  : '-'
              }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150" fixed="right">
            <template #default="{ row }">
              <el-button text type="primary" @click="viewDetail(row)">
                查看详情
              </el-button>
              <el-button
                text
                type="danger"
                @click="deleteRecord(row.id)"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 手机版卡片 -->
      <div v-if="publishHistory.length > 0" class="card-view">
        <div v-for="record in publishHistory" :key="record.id" class="history-record-card">
          <div class="record-header">
            <div class="record-title">{{ record.title }}</div>
            <el-tag :type="getStatusType(record.status)" size="small">
              {{ getStatusText(record.status) }}
            </el-tag>
          </div>

          <div class="record-body">
            <div class="info-row">
              <span class="label">平台：</span>
              <el-tag size="small">{{ getPlatformName(record.platform) }}</el-tag>
            </div>
            <div class="info-row">
              <span class="label">时间：</span>
              <span>{{
                record.status === 'scheduled' && record.scheduled_at
                  ? formatDate(record.scheduled_at)
                  : record.published_at
                  ? formatDate(record.published_at)
                  : '-'
              }}</span>
            </div>
          </div>

          <div class="record-actions">
            <el-button type="primary" text size="small" @click="viewDetail(record)">查看详情</el-button>
            <el-button type="danger" text size="small" @click="deleteRecord(record.id)">删除</el-button>
          </div>
        </div>
      </div>

      <el-empty v-else-if="!loading" description="暂无发布记录" />

      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        class="pagination"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
        </el-card>
      </div>
      <aside class="side-panel">
        <div class="panel">
          <h3 class="panel-title">发布流程</h3>
          <p class="panel-subtitle">快速推送到多平台</p>
          <div class="info-list">
            <div class="info-item">
              <div class="info-icon"><el-icon><Key /></el-icon></div>
              <div>
                <div class="info-title">绑定账号</div>
                <div class="info-desc">
                  前往<el-link type="primary" @click="router.push('/authorization')">账号授权</el-link>页面绑定平台账号。
                </div>
              </div>
            </div>
            <div class="info-item">
              <div class="info-icon"><el-icon><Upload /></el-icon></div>
              <div>
                <div class="info-title">选择内容</div>
                <div class="info-desc">支持文章、图片、视频等多类型内容。</div>
              </div>
            </div>
            <div class="info-item">
              <div class="info-icon"><el-icon><Clock /></el-icon></div>
              <div>
                <div class="info-title">设置发布</div>
                <div class="info-desc">可立即发布或设定时间。</div>
              </div>
            </div>
          </div>
        </div>
        <div class="panel">
          <h3 class="panel-title">快捷操作</h3>
          <div class="info-list">
            <div class="info-item">
              <div>
                <div class="info-title">平台账号</div>
                <div class="info-desc">
                  <el-button size="small" @click="router.push('/authorization')">
                    <el-icon><Key /></el-icon>
                    管理账号
                  </el-button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </aside>
    </section>

    <!-- 发布对话框 -->
    <el-dialog
      v-model="showPublishDialog"
      title="发布内容"
      width="800px"
      :close-on-click-modal="false"
    >
      <el-form :model="publishForm" :rules="publishRules" ref="publishFormRef" label-width="100px">
        <el-form-item label="选择内容" prop="creationId">
          <el-select
            v-model="publishForm.creationId"
            placeholder="选择要发布的内容"
            style="width: 100%"
            @change="handleCreationChange"
          >
            <el-option
              v-for="creation in creations"
              :key="creation.id"
              :label="creation.title"
              :value="creation.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="发布账号" prop="accountId">
          <el-select
            v-model="publishForm.accountId"
            placeholder="选择平台账号"
            style="width: 100%"
          >
            <el-option
              v-for="account in activePlatformAccounts"
              :key="account.id"
              :label="`${getPlatformName(account.platform)} - ${account.account_name}`"
              :value="account.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="发布方式" prop="publishType">
          <el-radio-group v-model="publishForm.publishType">
            <el-radio label="immediate">立即发布</el-radio>
            <el-radio label="scheduled">定时发布</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item
          v-if="publishForm.publishType === 'scheduled'"
          label="发布时间"
          prop="scheduledAt"
        >
          <el-date-picker
            v-model="publishForm.scheduledAt"
            type="datetime"
            placeholder="选择发布时间"
            :disabled-date="disabledDate"
          />
        </el-form-item>
        <el-form-item label="内容预览">
          <div class="content-preview" v-html="contentPreview"></div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showPublishDialog = false">取消</el-button>
        <el-button type="primary" @click="handlePublish" :loading="publishing">
          {{ publishForm.publishType === 'scheduled' ? '定时发布' : '立即发布' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Upload, Search, Key, Clock } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import { useRouter } from 'vue-router'
import {
  getPlatformAccounts,
  publishContent,
  getPublishHistory,
  deletePublishRecord,
} from '@/api/publish'
import { getCreations } from '@/api/creations'

const router = useRouter()

// 状态
const loading = ref(false)
const publishing = ref(false)
const showPublishDialog = ref(false)
const showDetailDialog = ref(false)
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 表单引用
const publishFormRef = ref<FormInstance>()

// 平台账号列表（只读，用于选择）
const platformAccounts = ref<any[]>([])

// 发布历史
const publishHistory = ref([])

// 创作列表
const creations = ref([])

// 当前记录
const currentRecord = ref(null)
const selectedCreation = ref<any>(null)

// 内容预览
const contentPreview = ref('')

// 发布表单
const publishForm = reactive({
  creationId: null,
  accountId: null,
  contentType: '',
  publishType: 'immediate',
  scheduledAt: null as Date | null,
})

// 表单验证规则
const publishRules: FormRules = {
  creationId: [{ required: true, message: '请选择要发布的内容', trigger: 'change' }],
  accountId: [{ required: true, message: '请选择发布账号', trigger: 'change' }],
  publishType: [{ required: true, message: '请选择发布方式', trigger: 'change' }],
  scheduledAt: [
    {
      validator: (_rule, value, callback) => {
        if (publishForm.publishType === 'scheduled' && !value) {
          callback(new Error('请选择发布时间'))
          return
        }
        callback()
      },
      trigger: 'change',
    },
  ],
}

// 计算属性
const activePlatformAccounts = computed(() =>
  platformAccounts.value.filter((account: any) => account.is_active === 'active' && account.cookies_valid === 'valid')
)

const successRate = computed(() => {
  if (publishHistory.value.length === 0) return 0
  const successCount = publishHistory.value.filter((h: any) => h.status === 'success').length
  return Math.round((successCount / publishHistory.value.length) * 100)
})

// 获取状态类型
const getStatusType = (status: string) => {
  const types: Record<string, any> = {
    draft: 'info',
    pending: 'info',
    publishing: 'warning',
    success: 'success',
    failed: 'danger'
  }
  return types[status] || 'info'
}

// 获取状态文本
const getStatusText = (status: string) => {
  const texts: Record<string, string> = {
    draft: '草稿',
    pending: '待发布',
    publishing: '发布中',
    success: '已发布',
    failed: '发布失败',
    scheduled: '已排期'
  }
  return texts[status] || '未知'
}

// 禁用日期
const disabledDate = (time: Date) => {
  return time.getTime() < Date.now()
}

const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}


// 加载平台账号列表（只读）
const loadPlatformAccounts = async () => {
  try {
    const response = await getPlatformAccounts()
    platformAccounts.value = response || []
  } catch (error: any) {
    console.error('加载平台账号失败:', error)
  }
}

// 初始化
onMounted(() => {
  loadPlatformAccounts()
  loadPublishHistory()
  loadCreations()
})
</script>

<style scoped lang="scss">
.publish-management {
  padding: 20px;
  background: linear-gradient(180deg, #f8fbff 0%, #ffffff 40%);
  --hero-from: rgba(59, 130, 246, 0.18);
  --hero-to: rgba(14, 165, 233, 0.18);
  --page-accent: #2563eb;

  :deep(.el-card) {
    border-radius: 14px;
    border: 1px solid #edf2f7;
    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.04);
  }

  .header-card {
    margin-bottom: 20px;
    background: linear-gradient(135deg, #eff6ff 0%, #f5f3ff 100%);

    .header-content {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;

      .header-left {
        h2 {
          margin: 0 0 8px 0;
          font-size: 24px;
          font-weight: 600;
          color: #1f2937;
        }

        .subtitle {
          margin: 0;
          color: #64748b;
          font-size: 14px;
        }
      }
    }
  }

  .history-card {
    .search-input {
      width: 200px;
    }

    .pagination {
      display: flex;
      justify-content: flex-end;
      margin-top: 20px;
    }

    .history-record-card {
      background: #fff;
      border: 1px solid #edf2f7;
      border-radius: 12px;
      padding: 16px;
      margin-bottom: 12px;

      .record-header {
        display: flex;
        justify-content: space-between;
        align-items: start;
        margin-bottom: 12px;

        .record-title {
          font-weight: 600;
          color: #1f2937;
          flex: 1;
          word-break: break-word;
          margin-right: 8px;
        }
      }

      .record-body {
        margin-bottom: 12px;

        .info-row {
          display: flex;
          justify-content: space-between;
          font-size: 13px;
          margin-bottom: 6px;
          color: #64748b;

          .label {
            color: #94a3b8;
          }
        }
      }

      .record-actions {
        display: flex;
        gap: 8px;
        padding-top: 12px;
        border-top: 1px solid #f1f5f9;
        justify-content: flex-end;
      }
      }
    }
  }

  .content-preview {
    max-height: 400px;
    overflow-y: auto;
    padding: 16px;
    background-color: #f5f7fa;
    border-radius: 4px;
    line-height: 1.8;

    :deep(img) {
      max-width: 100%;
      height: auto;
    }

    :deep(pre) {
      background-color: #282c34;
      color: #abb2bf;
      padding: 16px;
      border-radius: 4px;
      overflow-x: auto;
    }

    :deep(code) {
      background-color: #f0f0f0;
      padding: 2px 6px;
      border-radius: 3px;
      font-family: 'Courier New', monospace;
    }
  }
}

// 响应式适配
@media (max-width: 992px) {
  .publish-management {
    padding: 12px;

    .header-card {
      .header-content {
        flex-direction: column;
        gap: 12px;

        .header-left {
          h2 {
            font-size: 20px;
          }
        }
      }
    }

    .history-card {
      .card-header {
        flex-direction: column;
        align-items: flex-start;

        .search-input {
          width: 100%;
        }
      }

      .table-view {
        display: none;
      }

      .card-view {
        display: block;
      }
    }
  }
}

@media (max-width: 600px) {
  .publish-management {
    padding: 8px;

    .history-card {
      .pagination {
        flex-wrap: wrap;
        justify-content: center;
      }
    }
  }
}
</style>

