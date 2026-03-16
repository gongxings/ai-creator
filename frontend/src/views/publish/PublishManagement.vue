<template>
  <div class="publish-management">
    <el-card class="header-card">
      <div class="header-content">
        <div class="header-left">
          <h2>发布管理</h2>
          <p class="subtitle">一站式发布到多个平台</p>
        </div>
        <el-button type="primary" @click="showPublishDialog = true">
          <el-icon>
            <Upload/>
          </el-icon>
          新建发布
        </el-button>
      </div>
    </el-card>

    <!-- 平台账号管理 -->
    <el-card class="platforms-card">
      <template #header>
        <div class="card-header">
          <span>平台账号</span>
          <el-button text type="primary" @click="openBindDialog">
            <el-icon>
              <Plus/>
            </el-icon>
            绑定账号
          </el-button>
        </div>
      </template>

      <!-- 桌面版表格 -->
      <div class="table-view">
        <el-table :data="platformAccounts" v-loading="loadingAccounts" style="width: 100%">
          <el-table-column label="平台" width="160">
            <template #default="{ row }">
              {{ getPlatformName(row.platform) }}
            </template>
          </el-table-column>
          <el-table-column prop="account_name" label="账号名称" min-width="180"/>
          <el-table-column label="Cookie状态" width="120">
            <template #default="{ row }">
              <el-tag :type="getCookieStatusType(row.cookies_valid)">
                {{ getCookieStatusText(row.cookies_valid) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="Cookie更新时间" width="180">
            <template #default="{ row }">
              {{ row.cookies_updated_at ? formatDate(row.cookies_updated_at) : '-' }}
            </template>
          </el-table-column>
          <el-table-column label="账号状态" width="120">
            <template #default="{ row }">
              <el-tag :type="row.is_active === 'active' ? 'success' : 'info'">
                {{ row.is_active === 'active' ? '启用' : '禁用' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="240" fixed="right">
            <template #default="{ row }">
              <el-button size="small" type="primary" @click="openBindDialogWithPreselect(row)">
                绑定账号
              </el-button>
              <el-button size="small" @click="openCookieDialog(row)">更新Cookie</el-button>
              <el-button size="small" @click="handleValidateCookies(row)">验证</el-button>
              <el-button size="small" type="danger" @click="unbindPlatform(row.id)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 手机版卡片 -->
      <div v-if="platformAccounts.length > 0" class="card-view">
        <div v-for="account in platformAccounts" :key="account.id" class="platform-card">
          <div class="card-header">
            <div class="platform-info">
              <el-tag>{{ getPlatformName(account.platform) }}</el-tag>
              <span class="account-name">{{ account.account_name }}</span>
            </div>
            <el-tag :type="account.is_active === 'active' ? 'success' : 'info'" size="small">
              {{ account.is_active === 'active' ? '启用' : '禁用' }}
            </el-tag>
          </div>
          <div class="card-body">
            <div class="info-row">
              <span class="label">Cookie状态:</span>
              <el-tag :type="getCookieStatusType(account.cookies_valid)" size="small">
                {{ getCookieStatusText(account.cookies_valid) }}
              </el-tag>
            </div>
            <div class="info-row">
              <span class="label">更新时间:</span>
              <span>{{ account.cookies_updated_at ? formatDate(account.cookies_updated_at) : '-' }}</span>
            </div>
          </div>
          <div class="card-actions">
            <el-button type="primary" size="small" @click="openBindDialogWithPreselect(account)">绑定账号</el-button>
            <el-button size="small" @click="openCookieDialog(account)">更新Cookie</el-button>
            <el-button size="small" @click="handleValidateCookies(account)">验证</el-button>
            <el-button type="danger" size="small" plain @click="unbindPlatform(account.id)">删除</el-button>
          </div>
        </div>
      </div>

      <el-empty v-else-if="!loadingAccounts" description="暂无平台账号">
        <el-button type="primary" @click="openBindDialog">绑定账号</el-button>
      </el-empty>

    </el-card>

    <!-- 发布历史 -->
    <el-card class="history-card">
      <template #header>
        <div class="card-header">
          <span>发布历史</span>
          <el-input
              v-model="searchKeyword"
              placeholder="搜索关键词"
              class="search-input"
              clearable
              @input="handleSearch"
          >
            <template #prefix>
              <el-icon>
                <Search/>
              </el-icon>
            </template>
          </el-input>
        </div>
      </template>

      <!-- 桌面版表格 -->
      <div class="table-view">
        <el-table :data="publishHistory" v-loading="loading">
          <el-table-column prop="title" label="标题" min-width="200"/>
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
              <span class="label">平台:</span>
              <el-tag size="small">{{ getPlatformName(record.platform) }}</el-tag>
            </div>
            <div class="info-row">
              <span class="label">时间:</span>
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

      <el-empty v-else-if="!loading" description="暂无发布记录"/>
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
              placeholder="请选择要发布的内容"
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
              placeholder="请选择平台账号"
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
              placeholder="请选择发布时间"
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

    <!-- 绑定平台账号对话框 -->
    <el-dialog
        v-model="showBindDialog"
        title="绑定平台账号"
        width="600px"
        :close-on-click-modal="false"
    >
      <el-alert
          title="授权方式说明"
          type="info"
          :closable="false"
          style="margin-bottom: 20px"
      >
<!--        <p><strong>方式1: 自动授权</strong></p>-->
<!--        <ul>-->
<!--          <li>点击"自动授权"按钮，后台会打开浏览器窗口</li>-->
<!--          <li>在浏览器窗口中扫码/登录平台</li>-->
<!--          <li>登录成功后Cookie会自动提取</li>-->
<!--          <li>注意：需要服务器支持显示浏览器窗口</li>-->
<!--        </ul>-->
<!--        <p><strong>方式: 手动授权</strong></p>-->
<!--        <ul>-->
<!--          <li>点击"打开登录页面"按钮，登录对应平台</li>-->
<!--          <li>登录成功后，按F12打开开发者工具</li>-->
<!--          <li>切换到 Application / Storage → Cookies</li>-->
<!--          <li>复制该平台的所有Cookie</li>-->
<!--          <li>粘贴到下方输入框</li>-->
<!--          <li>点击"手动授权"按钮提交</li>-->
<!--        </ul>-->
        <ol style="margin: 0; padding-left: 20px; line-height: 1.8;">
          <li>点击下方"打开登录页面"按钮，在新窗口中登录{{ getPlatformName(bindForm.platformCode) }}</li>
          <li>登录成功后，按 <strong>F12</strong> 打开开发者工具</li>
          <li>切换到 <strong>Application</strong> 或 <strong>Storage</strong> 标签</li>
          <li>左侧选择 <strong>Cookies</strong> → 找到对应平台域名</li>
          <li>在 cookie 列表上<strong>右键 → 复制</strong> 或 全选复制</li>
          <li>粘贴到上方输入框</li>
        </ol>
      </el-alert>

      <el-tabs v-model="authMethod">
<!--        <el-tab-pane label="自动授权" name="frontend">-->
<!--          <div class="auth-frontend">-->
<!--            <el-form-item label="选择平台" prop="platformCode">-->
<!--              <el-select-->
<!--                  v-model="bindForm.platformCode"-->
<!--                  placeholder="请选择平台"-->
<!--                  style="width: 100%"-->
<!--                  @change="handlePlatformChange"-->
<!--              >-->
<!--                <el-option-->
<!--                    v-for="platform in platforms"-->
<!--                    :key="platform.platform"-->
<!--                    :label="platform.name"-->
<!--                    :value="platform.platform"-->
<!--                />-->
<!--              </el-select>-->
<!--            </el-form-item>-->

<!--            <el-form-item label="账号名称" prop="accountName">-->
<!--              <el-input v-model="bindForm.accountName" placeholder="请输入账号名称（用于区分不同账号）" />-->
<!--            </el-form-item>-->
<!--          </div>-->

<!--          <el-button-->
<!--              type="primary"-->
<!--              @click="handleFrontendAuth"-->
<!--              :loading="binding"-->
<!--              style="width: 100%; margin-top: 20px"-->
<!--              size="large"-->
<!--          >-->
<!--            自动授权-->
<!--          </el-button>-->
<!--        </el-tab-pane>-->

        <el-tab-pane label="手动授权" name="backend">
          <el-form ref="bindFormRef" :model="bindForm" :rules="bindRules" label-width="100px">
            <el-form-item label="选择平台" prop="platformCode">
              <el-select
                  v-model="bindForm.platformCode"
                  placeholder="请选择要绑定的平台"
                  style="width: 100%"
                  @change="handlePlatformChange"
              >
                <el-option
                    v-for="platform in platforms"
                    :key="platform.platform"
                    :label="platform.name"
                    :value="platform.platform"
                />
              </el-select>
            </el-form-item>

            <el-form-item label="账号名称" prop="accountName">
              <el-input v-model="bindForm.accountName" placeholder="请输入账号名称"/>
            </el-form-item>

            <el-form-item label="授权方式">
              <el-radio-group v-model="bindForm.authMode">
<!--                <el-radio-button label="auto">自动</el-radio-button>-->
                <el-radio-button label="manual">手动</el-radio-button>
              </el-radio-group>
            </el-form-item>

            <el-alert
                v-if="bindForm.authMode === 'auto'"
                title="点击【手动授权】按钮，按照说明操作"
                type="info"
                :closable="false"
                show-icon
            />

            <el-form-item v-if="bindForm.authMode === 'manual'" label="Cookie" prop="cookies">
              <el-input
                  v-model="bindForm.cookies"
                  type="textarea"
                  :rows="4"
                  placeholder="粘贴从浏览器开发者工具复制的Cookie字符串（如：key=value; key2=value2）"
              />
            </el-form-item>

            <!-- Cookie获取教程 -->
            <el-alert
                v-if="bindForm.authMode === 'manual'"
                title="如何获取Cookie"
                type="info"
                :closable="false"
                style="margin-top: 15px"
            >
              <template #default>
                <div class="cookie-help">
                  <el-button 
                    type="primary" 
                    size="small" 
                    style="margin-top: 12px"
                    @click="openLoginPage"
                    :disabled="!bindForm.platformCode"
                  >
                    打开登录页面
                  </el-button>
                </div>
              </template>
            </el-alert>

            <el-button
                type="primary"
                @click="handleBind"
                :loading="binding"
                style="width: 100%; margin-top: 20px"
                size="large"
            >
              手动授权
            </el-button>
          </el-form>
        </el-tab-pane>
      </el-tabs>

      <template #footer>
        <el-button @click="showBindDialog = false">取消</el-button>
      </template>
    </el-dialog>

    <!-- 更新Cookie对话框 -->
    <el-dialog
        v-model="showCookieDialog"
        title="更新Cookie"
        width="600px"
        :close-on-click-modal="false"
    >
      <el-form :model="cookieForm" :rules="cookieRules" ref="cookieFormRef" label-width="100px">
        <el-form-item label="平台账号">
          <span>{{ cookieForm.accountLabel }}</span>
        </el-form-item>

        <el-form-item label="Cookie" prop="cookies">
          <el-input
              v-model="cookieForm.cookies"
              type="textarea"
              :rows="4"
              placeholder="粘贴Cookie字符串（如：key=value; key2=value2）或JSON格式"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showCookieDialog = false">取消</el-button>
        <el-button type="primary" @click="handleUpdateCookies" :loading="updatingCookies">
          更新
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
          {{
            currentRecord.status === 'scheduled' && currentRecord.scheduled_at
                ? formatDate(currentRecord.scheduled_at)
                : currentRecord.published_at
                    ? formatDate(currentRecord.published_at)
                    : '-'
          }}
        </el-descriptions-item>
        <el-descriptions-item label="发布平台">
          <el-tag size="small">
            {{ getPlatformName(currentRecord.platform) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="账号名称">
          {{ currentRecord.account_name || '-' }}
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>

  </div>
</template>

<script setup lang="ts">
import {ref, reactive, computed, onMounted, onUnmounted} from 'vue'
import {ElMessage, ElMessageBox} from 'element-plus'
import {Upload, Plus, Search} from '@element-plus/icons-vue'
import type {FormInstance, FormRules} from 'element-plus'

import {
  getPlatforms,
  getPlatformLoginInfo,
  createPlatformAccount,
  authorizePlatformAccount,
  updatePlatformCookies,
  validatePlatformCookies,
  getPlatformAccounts,
  deletePlatformAccount,
  publishContent,
  getPublishHistory,
  deletePublishRecord,
  submitPublishCookies
} from '@/api/publish'

import {getCreations} from '@/api/creations'

// 状态
const loading = ref(false)
const publishing = ref(false)
const binding = ref(false)
const updatingCookies = ref(false)
const loadingAccounts = ref(false)

const showPublishDialog = ref(false)
const showBindDialog = ref(false)
const showCookieDialog = ref(false)
const showDetailDialog = ref(false)

const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const loginInfo = ref<{ platform: string; name: string; login_url: string; instructions: string } | null>(null)

// 授权方式
const authMethod = ref('frontend')

// 表单引用
const publishFormRef = ref<FormInstance>()
const bindFormRef = ref<FormInstance>()
const cookieFormRef = ref<FormInstance>()

// 平台列表
const platforms = ref<any[]>([])
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

// 绑定表单
const bindForm = reactive({
  platformCode: '',
  accountName: '',
  cookies: '',
  authMode: 'manual'
})

// Cookie表单
const cookieForm = reactive({
  accountId: 0,
  accountLabel: '',
  cookies: ''
})

// 表单验证规则
const publishRules: FormRules = {
  creationId: [{required: true, message: '请选择要发布的内容', trigger: 'change'}],
  accountId: [{required: true, message: '请选择发布账号', trigger: 'change'}],
  publishType: [{required: true, message: '请选择发布方式', trigger: 'change'}],
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

const bindRules: FormRules = {
  platformCode: [{required: true, message: '请选择平台', trigger: 'change'}],
  accountName: [{
    required: true, message: '请输入账号名称', trigger: 'blur'
  }],
  cookies: [
    {
      validator: (_rule, value, callback) => {
        if (bindForm.authMode === 'manual' && !value) {
          callback(new Error('请输入Cookie'))
          return
        }
        callback()
      },
      trigger: 'blur',
    },
  ],
}

const cookieRules: FormRules = {
  cookies: [{required: true, message: '请输入Cookie', trigger: 'blur'}]
}

// 计算属性
const activePlatformAccounts = computed(() =>
    platformAccounts.value.filter((account: any) => account.is_active === 'active')
)

const getPlatformName = (code: string) => {
  const match = platforms.value.find((platform: any) => platform.platform === code)
  return match?.name || code
}

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
    scheduled: '已排期',
  }
  return texts[status] || '未知'
}

// 禁用日期（不能选择过去的时间）
const disabledDate = (time: Date) => {
  return time.getTime() < Date.now()
}

const getCookieStatusType = (status?: string | null) => {
  if (status === 'valid') return 'success'
  if (status === 'invalid') return 'danger'
  return 'info'
}

const getCookieStatusText = (status?: string | null) => {
  if (status === 'valid') return '有效'
  if (status === 'invalid') return '无效'
  return '未知'
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

// 加载平台列表
const loadPlatforms = async () => {
  try {
    const response = await getPlatforms()
    platforms.value = response || []
  } catch (error: any) {
    console.error('加载平台列表失败:', error)
    ElMessage.error(error.message || '加载平台列表失败')
  }
}

// 加载平台账号列表
const loadPlatformAccounts = async () => {
  loadingAccounts.value = true
  try {
    const response = await getPlatformAccounts()
    platformAccounts.value = response || []
  } catch (error: any) {
    console.error('加载平台账号失败:', error)
    ElMessage.error(error.message || '加载平台账号失败')
  } finally {
    loadingAccounts.value = false
  }
}

// 加载发布历史
const loadPublishHistory = async () => {
  loading.value = true
  try {
    const response = await getPublishHistory({
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value,
    })
    publishHistory.value = response.items
    total.value = response.total
  } catch (error: any) {
    console.error('加载发布历史失败:', error)
    ElMessage.error(error.message || '加载发布历史失败')
  } finally {
    loading.value = false
  }
}

// 加载创作列表
const loadCreations = async () => {
  try {
    const response = await getCreations({page: 1, page_size: 100})
    creations.value = response.items
  } catch (error: any) {
    console.error('加载创作列表失败:', error)
    ElMessage.error(error.message || '加载创作列表失败')
  }
}

// 搜索
const handleSearch = () => {
  currentPage.value = 1
  loadPublishHistory()
}

// 分页大小改变
const handleSizeChange = (size: number) => {
  pageSize.value = size
  loadPublishHistory()
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page
  loadPublishHistory()
}

// 选择内容改变
const handleCreationChange = (creationId: number) => {
  const creation = creations.value.find((c: any) => c.id === creationId)
  if (creation) {
    selectedCreation.value = creation
    contentPreview.value = creation.content
    publishForm.contentType = creation.content_type
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
          account_id: publishForm.accountId!,
          creation_id: publishForm.creationId!,
          content_type: publishForm.contentType,
          scheduled_at:
              publishForm.publishType === 'scheduled' && publishForm.scheduledAt
                  ? publishForm.scheduledAt.toISOString()
                  : undefined,
          title: selectedCreation.value?.title,
          content: selectedCreation.value?.content,
        })
        ElMessage.success('发布成功')
        showPublishDialog.value = false
        publishForm.publishType = 'immediate'
        publishForm.scheduledAt = null
        loadPublishHistory()
      } catch (error: any) {
        console.error('发布失败:', error)
        ElMessage.error(error.message || '发布失败')
      } finally {
        publishing.value = false
      }
    }
  })
}

// 将Cookie字符串转换为对象
const parseCookieString = (cookieStr: string): Record<string, string> => {
  const cookies: Record<string, string> = {}
  if (!cookieStr) return cookies
  
  const pairs = cookieStr.split(';')
  for (const pair of pairs) {
    const [name, ...valueParts] = pair.split('=')
    if (name && valueParts.length > 0) {
      const value = valueParts.join('=').trim()
      cookies[name.trim()] = value
    }
  }
  return cookies
}

const openBindDialog = () => {
  bindForm.platformCode = ''
  bindForm.accountName = ''
  bindForm.cookies = ''
  bindForm.authMode = 'auto'
  loginInfo.value = null
  authMethod.value = 'frontend'
  showBindDialog.value = true
}

// 打开绑定对话框并预填充平台和账号信息
const openBindDialogWithPreselect = (row: any) => {
  bindForm.platformCode = row.platform
  bindForm.accountName = row.account_name || ''
  bindForm.cookies = ''
  bindForm.authMode = 'auto'
  loginInfo.value = null
  authMethod.value = 'frontend'
  showBindDialog.value = true
}

// 打开平台登录页面
const openLoginPage = () => {
  if (!bindForm.platformCode) {
    ElMessage.warning('请先选择平台')
    return
  }
  // 这里使用一个简单的方式：直接打开平台的登录URL
  // 实际URL可以从后端API获取或硬编码映射
  const platformLoginUrls: Record<string, string> = {
    wechat: 'https://mp.weixin.qq.com/',
    xiaohongshu: 'https://creator.xiaohongshu.com/login',
    douyin: 'https://creator.douyin.com/',
    kuaishou: 'https://cp.kuaishou.com/',
    toutiao: 'https://mp.toutiao.com/',
    zhihu: 'https://www.zhihu.com/signin',
    jianshu: 'https://www.jianshu.com/sign_in',
    baijiahao: 'https://baijiahao.baidu.com/'
  }
  const url = platformLoginUrls[bindForm.platformCode]
  if (url) {
    window.open(url, '_blank')
  } else {
    ElMessage.error('该平台登录地址未配置')
  }
}

const handlePlatformChange = async (platformCode: string) => {
  if (!platformCode) {
    loginInfo.value = null
    return
  }
  try {
    const response = await getPlatformLoginInfo(platformCode)
    loginInfo.value = response
  } catch (error: any) {
    loginInfo.value = null
    ElMessage.error(error.message || '获取登录信息失败')
  }
}

// 前端授权（改进：直接调用后端Playwright自动授权）
const handleFrontendAuth = async () => {
  if (!bindForm.platformCode) {
    ElMessage.warning('请选择平台')
    return
  }

  if (!bindForm.accountName) {
    ElMessage.warning('请输入账号名称')
    return
  }

  binding.value = true
  try {
    // 直接调用后端Playwright自动授权
    // 后端会打开一个可见的浏览器窗口，用户扫码登录后自动提取Cookie
    await authorizePlatformAccount({
      platform: bindForm.platformCode,
      account_name: bindForm.accountName
    })

    ElMessage.success('授权成功！Cookie已自动获取')
    // 刷新账号列表
    await loadPlatformAccounts()
    // 关闭对话框
    showBindDialog.value = false
    bindForm.platformCode = ''
    bindForm.accountName = ''
    bindForm.cookies = ''
    loginInfo.value = null
  } catch (error: any) {
    console.error('授权失败:', error)
    ElMessage.error(error.message || '授权失败，请重试')
  } finally {
    binding.value = false
  }
}

// 绑定
const handleBind = async () => {
  if (authMethod.value === 'frontend') {
    // 前端授权方案
    handleFrontendAuth()
    return
  }

  // 后端授权方案或手动
  if (!bindFormRef.value) return
  await bindFormRef.value.validate(async (valid) => {
    if (valid) {
      binding.value = true
      try {
        if (bindForm.authMode === 'auto') {
          // 后端Playwright自动授权
          await authorizePlatformAccount({
            platform: bindForm.platformCode,
            account_name: bindForm.accountName,
          })
          ElMessage.success('授权成功，已自动提取Cookie')
        } else {
          // 手动提交Cookie（支持JSON对象或标准Cookie字符串）
          let cookies: Record<string, string> = {}
          // 先尝试解析为JSON对象
          try {
            cookies = JSON.parse(bindForm.cookies)
          } catch {
            // 如果不是JSON，按Cookie字符串解析
            cookies = parseCookieString(bindForm.cookies)
          }

          if (Object.keys(cookies).length === 0) {
            ElMessage.error('Cookie格式错误或为空')
            binding.value = false
            return
          }

          const accountResponse = await createPlatformAccount({
            platform: bindForm.platformCode,
            account_name: bindForm.accountName,
          })

          const updateResponse = await updatePlatformCookies(accountResponse.id, cookies)

          if (updateResponse.valid) {
            ElMessage.success('绑定成功，Cookie有效')
          } else {
            ElMessage.warning(updateResponse.message || '绑定成功，但Cookie验证失败')
          }
        }

        showBindDialog.value = false
        bindForm.platformCode = ''
        bindForm.accountName = ''
        bindForm.cookies = ''
        loginInfo.value = null
        loadPlatformAccounts()

      } catch (error: any) {
        console.error('绑定失败:', error)
        ElMessage.error(error.message || '绑定失败')
      } finally {
        binding.value = false
      }
    }
  })
}

const handleAutoAuthorize = async (row: any) => {
  try {
    binding.value = true
    await authorizePlatformAccount({
      platform: row.platform,
      account_name: row.account_name,
    })
    ElMessage.success('授权成功，已自动提取Cookie')
    loadPlatformAccounts()
  } catch (error: any) {
    console.error('自动授权失败:', error)
    ElMessage.error(error.response?.data?.detail || error.message || '自动授权失败')
  } finally {
    binding.value = false
  }
}

const openCookieDialog = (row: any) => {
  cookieForm.accountId = row.id
  cookieForm.accountLabel = `${getPlatformName(row.platform)} - ${row.account_name}`
  cookieForm.cookies = ''
  showCookieDialog.value = true
}

const handleUpdateCookies = async () => {
  if (!cookieFormRef.value) return
  await cookieFormRef.value.validate(async (valid) => {
    if (!valid) return
    updatingCookies.value = true
    try {
      let cookies: Record<string, string> = {}
      // 先尝试解析为JSON对象
      try {
        cookies = JSON.parse(cookieForm.cookies)
      } catch {
        // 如果不是JSON，按Cookie字符串解析
        cookies = parseCookieString(cookieForm.cookies)
      }

      if (Object.keys(cookies).length === 0) {
        ElMessage.error('Cookie格式错误或为空')
        updatingCookies.value = false
        return
      }

      const response = await updatePlatformCookies(cookieForm.accountId, cookies)
      if (response.valid) {
        ElMessage.success('Cookie更新成功')
      } else {
        ElMessage.warning(response.message || 'Cookie更新失败')
      }

      showCookieDialog.value = false
      loadPlatformAccounts()
    } catch (error: any) {
      console.error('更新Cookie失败:', error)
      ElMessage.error(error.message || '更新Cookie失败')
    } finally {
      updatingCookies.value = false
    }
  })
}

const handleValidateCookies = async (row: any) => {
  try {
    const response = await validatePlatformCookies(row.id)
    if (response.valid) {
      ElMessage.success('Cookie有效')
    } else {
      ElMessage.warning(response.message || 'Cookie已失效')
    }
    loadPlatformAccounts()
  } catch (error: any) {
    console.error('验证Cookie失败:', error)
    ElMessage.error(error.message || '验证Cookie失败')
  }
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
    loadPlatformAccounts()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('解绑失败:', error)
      ElMessage.error(error.message || '解绑失败')
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
      ElMessage.error(error.message || '删除失败')
    }
  }
}

// 初始化
onMounted(() => {
  loadPlatforms()
  loadPlatformAccounts()
  loadPublishHistory()
  loadCreations()
})

</script>

<style scoped lang="scss">
.publish-management {
  padding: 20px;
  background: linear-gradient(180deg, #f8fbff 0%, #ffffff 40%);

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

  .platforms-card,
  .history-card {
    margin-bottom: 20px;

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 12px;
    }

    // 表格视图
    .table-view {
      display: block;
    }

    // 卡片视图
    .card-view {
      display: none;
    }
  }

  .platforms-card {
    .platform-card {
      background: #fff;
      border: 1px solid #edf2f7;
      border-radius: 12px;
      padding: 16px;
      margin-bottom: 12px;

      .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;

        .platform-info {
          display: flex;
          align-items: center;
          gap: 10px;

          .account-name {
            font-weight: 600;
            color: #1f2937;
          }
        }
      }

      .card-body {
        margin-bottom: 12px;

        .info-row {
          display: flex;
          justify-content: space-between;
          font-size: 13px;
          margin-bottom: 8px;
          color: #64748b;

          .label {
            color: #94a3b8;
          }
        }
      }

      .card-actions {
        display: flex;
        gap: 8px;
        padding-top: 12px;
        border-top: 1px solid #f1f5f9;
        justify-content: flex-end;
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

  .login-info {
    margin-top: 8px;
    display: flex;
    flex-direction: column;
    gap: 6px;

    a {
      color: #409eff;
    }
  }
}

// 响应式布局
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

    .platforms-card,
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

    .platforms-card {
      .platform-card {
        .card-actions {
          flex-wrap: wrap;
        }
      }
    }

    .history-card {
      .pagination {
        flex-wrap: wrap;
        justify-content: center;
      }

      .history-record-card {
        .record-header {
          flex-direction: column;

          .record-title {
            margin-right: 0;
            margin-bottom: 8px;
          }
        }

        .record-actions {
          justify-content: space-between;
        }
      }
    }
  }
}
</style>