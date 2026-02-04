<template>
  <div class="publish-management">
    <el-card class="header-card">
      <div class="header-content">
        <div>
          <h2>发布管理</h2>
          <p class="subtitle">一键发布到多个平台</p>
        </div>
        <el-button type="primary" @click="showPublishDialog = true">
          <el-icon><Upload /></el-icon>
          新建发布
        </el-button>
      </div>
    </el-card>

    <!-- 平台账号管理 -->
    <el-card class="platforms-card">
      <template #header>
        <div class="card-header">
          <span>平台账号</span>
          <el-button text @click="showBindDialog = true">
            <el-icon><Plus /></el-icon>
            绑定账号
          </el-button>
        </div>
      </template>
      <div class="platforms-grid">
        <div
          v-for="platform in platforms"
          :key="platform.id"
          class="platform-card"
          :class="{ bound: platform.isBound }"
        >
          <div class="platform-icon">
            <el-icon :size="32">
              <component :is="getPlatformIcon(platform.code)" />
            </el-icon>
          </div>
          <div class="platform-info">
            <h4>{{ platform.name }}</h4>
            <p v-if="platform.isBound" class="bound-status">
              <el-icon color="#67c23a"><CircleCheck /></el-icon>
              已绑定
            </p>
            <p v-else class="unbound-status">
              <el-icon color="#909399"><CircleClose /></el-icon>
              未绑定
            </p>
          </div>
          <div class="platform-actions">
            <el-button
              v-if="platform.isBound"
              text
              type="danger"
              @click="unbindPlatform(platform.id)"
            >
              解绑
            </el-button>
            <el-button
              v-else
              text
              type="primary"
              @click="bindPlatform(platform.code)"
            >
              绑定
            </el-button>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 发布历史 -->
    <el-card class="history-card">
      <template #header>
        <div class="card-header">
          <span>发布历史</span>
          <el-input
            v-model="searchKeyword"
            placeholder="搜索标题"
            style="width: 200px"
            clearable
            @input="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </div>
      </template>
      <el-table :data="publishHistory" v-loading="loading">
        <el-table-column prop="title" label="标题" min-width="200" />
        <el-table-column prop="platforms" label="发布平台" width="200">
          <template #default="{ row }">
            <el-tag
              v-for="platform in row.platforms"
              :key="platform"
              size="small"
              style="margin-right: 5px"
            >
              {{ platform }}
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
        <el-table-column prop="publishTime" label="发布时间" width="180" />
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
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </el-card>

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
        <el-form-item label="发布平台" prop="platformIds">
          <el-checkbox-group v-model="publishForm.platformIds">
            <el-checkbox
              v-for="platform in boundPlatforms"
              :key="platform.id"
              :label="platform.id"
            >
              {{ platform.name }}
            </el-checkbox>
          </el-checkbox-group>
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
          prop="scheduledTime"
        >
          <el-date-picker
            v-model="publishForm.scheduledTime"
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
          {{ publishForm.publishType === 'immediate' ? '立即发布' : '定时发布' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 绑定平台对话框 -->
    <el-dialog
      v-model="showBindDialog"
      title="绑定平台账号"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form :model="bindForm" :rules="bindRules" ref="bindFormRef" label-width="100px">
        <el-form-item label="选择平台" prop="platformCode">
          <el-select
            v-model="bindForm.platformCode"
            placeholder="选择要绑定的平台"
            style="width: 100%"
          >
            <el-option
              v-for="platform in unboundPlatforms"
              :key="platform.code"
              :label="platform.name"
              :value="platform.code"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="账号名称" prop="accountName">
          <el-input v-model="bindForm.accountName" placeholder="输入账号名称" />
        </el-form-item>
        <el-form-item label="认证信息" prop="credentials">
          <el-input
            v-model="bindForm.credentials"
            type="textarea"
            :rows="4"
            placeholder="输入平台API密钥或认证信息（JSON格式）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showBindDialog = false">取消</el-button>
        <el-button type="primary" @click="handleBind" :loading="binding">
          绑定
        </el-button>
      </template>
    </el-dialog>

    <!-- 详情对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      title="发布详情"
      width="800px"
    >
      <el-descriptions :column="2" border v-if="currentRecord">
        <el-descriptions-item label="标题">
          {{ currentRecord.title }}
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(currentRecord.status)">
            {{ getStatusText(currentRecord.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="发布时间">
          {{ currentRecord.publishTime }}
        </el-descriptions-item>
        <el-descriptions-item label="发布平台">
          <el-tag
            v-for="platform in currentRecord.platforms"
            :key="platform"
            size="small"
            style="margin-right: 5px"
          >
            {{ platform }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="内容" :span="2">
          <div class="content-preview" v-html="currentRecord.content"></div>
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Upload,
  Plus,
  Search,
  CircleCheck,
  CircleClose,
  ChatDotRound,
  Picture,
  VideoCamera,
  Document
} from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import {
  getPlatforms,
  bindPlatformAccount,
  getPlatformAccounts,
  deletePlatformAccount,
  publishContent,
  getPublishHistory,
  deletePublishRecord
} from '@/api/publish'
import { getCreations } from '@/api/creations'

// 状态
const loading = ref(false)
const publishing = ref(false)
const binding = ref(false)
const showPublishDialog = ref(false)
const showBindDialog = ref(false)
const showDetailDialog = ref(false)
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 表单引用
const publishFormRef = ref<FormInstance>()
const bindFormRef = ref<FormInstance>()

// 平台列表
const platforms = ref([
  { id: 1, code: 'wechat', name: '微信公众号', isBound: false },
  { id: 2, code: 'xiaohongshu', name: '小红书', isBound: false },
  { id: 3, code: 'douyin', name: '抖音', isBound: false },
  { id: 4, code: 'kuaishou', name: '快手', isBound: false },
  { id: 5, code: 'toutiao', name: '今日头条', isBound: false },
  { id: 6, code: 'zhihu', name: '知乎', isBound: false }
])

// 发布历史
const publishHistory = ref([])

// 创作列表
const creations = ref([])

// 当前记录
const currentRecord = ref(null)

// 内容预览
const contentPreview = ref('')

// 发布表单
const publishForm = reactive({
  creationId: null,
  platformIds: [],
  publishType: 'immediate',
  scheduledTime: null
})

// 绑定表单
const bindForm = reactive({
  platformCode: '',
  accountName: '',
  credentials: ''
})

// 表单验证规则
const publishRules: FormRules = {
  creationId: [{ required: true, message: '请选择要发布的内容', trigger: 'change' }],
  platformIds: [{ required: true, message: '请选择发布平台', trigger: 'change' }],
  publishType: [{ required: true, message: '请选择发布方式', trigger: 'change' }],
  scheduledTime: [{ required: true, message: '请选择发布时间', trigger: 'change' }]
}

const bindRules: FormRules = {
  platformCode: [{ required: true, message: '请选择平台', trigger: 'change' }],
  accountName: [{ required: true, message: '请输入账号名称', trigger: 'blur' }],
  credentials: [{ required: true, message: '请输入认证信息', trigger: 'blur' }]
}

// 计算属性
const boundPlatforms = computed(() => platforms.value.filter(p => p.isBound))
const unboundPlatforms = computed(() => platforms.value.filter(p => !p.isBound))

// 获取平台图标
const getPlatformIcon = (code: string) => {
  const icons: Record<string, any> = {
    wechat: ChatDotRound,
    xiaohongshu: Picture,
    douyin: VideoCamera,
    kuaishou: VideoCamera,
    toutiao: Document,
    zhihu: Document
  }
  return icons[code] || Document
}

// 获取状态类型
const getStatusType = (status: string) => {
  const types: Record<string, any> = {
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
    pending: '待发布',
    publishing: '发布中',
    success: '已发布',
    failed: '发布失败'
  }
  return texts[status] || '未知'
}

// 禁用日期
const disabledDate = (time: Date) => {
  return time.getTime() < Date.now()
}

// 加载平台列表
const loadPlatforms = async () => {
  try {
    const response = await getPlatforms()
    const platformList = response.data
    
    // 获取已绑定的账号
    const accountsResponse = await getPlatformAccounts()
    const boundPlatformCodes = accountsResponse.data.map((acc: any) => acc.platform)
    
    // 更新平台绑定状态
    platforms.value = platforms.value.map(p => ({
      ...p,
      isBound: boundPlatformCodes.includes(p.code)
    }))
  } catch (error: any) {
    console.error('加载平台列表失败:', error)
    ElMessage.error(error.response?.data?.detail || '加载平台列表失败')
  }
}

// 加载发布历史
const loadPublishHistory = async () => {
  loading.value = true
  try {
    const response = await getPublishHistory({
      page: currentPage.value,
      page_size: pageSize.value,
    })
    publishHistory.value = response.data.items
    total.value = response.data.total
  } catch (error: any) {
    console.error('加载发布历史失败:', error)
    ElMessage.error(error.response?.data?.detail || '加载发布历史失败')
  } finally {
    loading.value = false
  }
}

// 加载创作列表
const loadCreations = async () => {
  try {
    const response = await getCreations({ page: 1, page_size: 100 })
    creations.value = response.data.items
  } catch (error: any) {
    console.error('加载创作列表失败:', error)
    ElMessage.error(error.response?.data?.detail || '加载创作列表失败')
  }
}

// 搜索
const handleSearch = () => {
  currentPage.value = 1
  loadPublishHistory()
}

// 分页
const handleSizeChange = (size: number) => {
  pageSize.value = size
  loadPublishHistory()
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page
  loadPublishHistory()
}

// 选择内容变化
const handleCreationChange = (creationId: number) => {
  const creation = creations.value.find((c: any) => c.id === creationId)
  if (creation) {
    contentPreview.value = creation.content
  }
}

// 发布
const handlePublish = async () => {
  if (!publishFormRef.value) return
  
  await publishFormRef.value.validate(async (valid) => {
    if (valid) {
      publishing.value = true
      try {
        await publishContent({
          creation_id: publishForm.creationId!,
          platform_ids: publishForm.platformIds,
          publish_type: publishForm.publishType,
          scheduled_time: publishForm.scheduledTime || undefined,
        })
        
        ElMessage.success('发布成功')
        showPublishDialog.value = false
        loadPublishHistory()
      } catch (error: any) {
        console.error('发布失败:', error)
        ElMessage.error(error.response?.data?.detail || '发布失败')
      } finally {
        publishing.value = false
      }
    }
  })
}

// 绑定平台
const bindPlatform = (code: string) => {
  bindForm.platformCode = code
  showBindDialog.value = true
}

// 处理绑定
const handleBind = async () => {
  if (!bindFormRef.value) return
  
  await bindFormRef.value.validate(async (valid) => {
    if (valid) {
      binding.value = true
      try {
        let credentials: Record<string, any> = {}
        try {
          credentials = JSON.parse(bindForm.credentials)
        } catch (e) {
          ElMessage.error('认证信息格式错误，请输入有效的JSON')
          binding.value = false
          return
        }
        
        await bindPlatformAccount({
          platform: bindForm.platformCode,
          account_name: bindForm.accountName,
          credentials,
        })
        
        ElMessage.success('绑定成功')
        showBindDialog.value = false
        loadPlatforms()
      } catch (error: any) {
        console.error('绑定失败:', error)
        ElMessage.error(error.response?.data?.detail || '绑定失败')
      } finally {
        binding.value = false
      }
    }
  })
}

// 解绑平台
const unbindPlatform = async (platformId: number) => {
  try {
    await ElMessageBox.confirm('确定要解绑该平台账号吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await deletePlatformAccount(platformId)
    
    ElMessage.success('解绑成功')
    loadPlatforms()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('解绑失败:', error)
      ElMessage.error(error.response?.data?.detail || '解绑失败')
    }
  }
}

// 查看详情
const viewDetail = (record: any) => {
  currentRecord.value = record
  showDetailDialog.value = true
}

// 删除记录
const deleteRecord = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定要删除该发布记录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await deletePublishRecord(id)
    
    ElMessage.success('删除成功')
    loadPublishHistory()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
}

// 初始化
onMounted(() => {
  loadPlatforms()
  loadPublishHistory()
  loadCreations()
})
</script>

<style scoped lang="scss">
.publish-management {
  padding: 20px;

  .header-card {
    margin-bottom: 20px;

    .header-content {
      display: flex;
      justify-content: space-between;
      align-items: center;

      h2 {
        margin: 0 0 8px 0;
        font-size: 24px;
        font-weight: 600;
      }

      .subtitle {
        margin: 0;
        color: #909399;
        font-size: 14px;
      }
    }
  }

  .platforms-card {
    margin-bottom: 20px;

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .platforms-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
      gap: 16px;

      .platform-card {
        padding: 20px;
        border: 1px solid #e4e7ed;
        border-radius: 8px;
        transition: all 0.3s;

        &:hover {
          box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
        }

        &.bound {
          border-color: #67c23a;
          background-color: #f0f9ff;
        }

        .platform-icon {
          margin-bottom: 12px;
          color: #409eff;
        }

        .platform-info {
          h4 {
            margin: 0 0 8px 0;
            font-size: 16px;
            font-weight: 600;
          }

          p {
            margin: 0;
            font-size: 14px;
            display: flex;
            align-items: center;
            gap: 4px;
          }

          .bound-status {
            color: #67c23a;
          }

          .unbound-status {
            color: #909399;
          }
        }

        .platform-actions {
          margin-top: 12px;
        }
      }
    }
  }

  .history-card {
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    :deep(.el-pagination) {
      margin-top: 20px;
      justify-content: flex-end;
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
</style>
