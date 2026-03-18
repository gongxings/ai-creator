<template>
  <div class="publish-page">
    <section class="hero">
      <div>
        <p class="eyebrow">Publish Center</p>
        <h1>内容发布</h1>
        <p class="desc">统一管理平台账号、发布动作和历史记录。</p>
      </div>
      <div class="hero-actions">
        <el-button @click="openBindDialog">绑定账号</el-button>
        <el-button type="primary" @click="showPublishDialog = true">
          <el-icon>
            <Upload/>
          </el-icon>
          新建发布
        </el-button>
      </div>
    </section>

    <section class="stats">
      <el-card class="glass">
        <div class="label">已绑定账号</div>
        <div class="value">{{ platformAccounts.length }}</div>
      </el-card>
      <el-card class="glass">
        <div class="label">可用账号</div>
        <div class="value">{{ activeAccounts.length }}</div>
      </el-card>
      <el-card class="glass">
        <div class="label">发布记录</div>
        <div class="value">{{ total }}</div>
      </el-card>
    </section>

    <el-card class="glass panel">
      <template #header>
        <div class="panel-head">
          <div><h3>平台账号</h3>
            <p>先绑定平台账号，再发起发布任务。</p></div>
          <el-button link type="primary" @click="loadPlatformAccounts">刷新</el-button>
        </div>
      </template>
      <div v-loading="loadingAccounts" class="account-grid">
        <div v-for="account in platformAccounts" :key="account.id" class="account-card">
          <div class="row top">
            <div><strong>{{ getPlatformName(account.platform) }}</strong><span>{{ account.account_name }}</span></div>
            <el-tag :type="account.is_active === 'active' ? 'success' : 'info'" effect="plain">
              {{ account.is_active === 'active' ? '启用中' : '已停用' }}
            </el-tag>
          </div>
          <div class="meta"><span>Cookie 状态</span>
            <el-tag :type="getCookieStatusType(account.cookies_valid)" size="small" effect="plain">
              {{ getCookieStatusText(account.cookies_valid) }}
            </el-tag>
          </div>
          <div class="meta"><span>最近更新</span><span>{{
              account.cookies_updated_at ? formatDate(account.cookies_updated_at) : '暂无记录'
            }}</span></div>
          <div class="actions">
            <el-button size="small" @click="openBindDialogWithPreselect(account)">重新授权</el-button>
            <el-button size="small" @click="openCookieDialog(account)">更新 Cookie</el-button>
            <el-button size="small" @click="handleValidateCookies(account)">验证</el-button>
            <el-button size="small" type="danger" plain @click="unbindPlatform(account.id)">删除</el-button>
          </div>
        </div>
        <el-empty v-if="!loadingAccounts && !platformAccounts.length" description="暂无平台账号"/>
      </div>
    </el-card>

    <el-card class="glass panel">
      <template #header>
        <div class="panel-head panel-head-row">
          <div><h3>发布记录</h3>
            <p>查看近期发布状态和平台详情。</p></div>
          <div class="toolbar">
            <el-input v-model="searchKeyword" placeholder="搜索标题或平台" clearable class="search">
              <template #prefix>
                <el-icon>
                  <Search/>
                </el-icon>
              </template>
            </el-input>
            <el-button link type="primary" @click="loadPublishHistory">刷新</el-button>
          </div>
        </div>
      </template>
      <div v-loading="loading" class="history-list">
        <div v-for="record in filteredHistory" :key="record.id" class="history-item">
          <div><strong>{{ record.title || '未命名内容' }}</strong>
            <div class="sub">
              <el-tag size="small" effect="plain">{{ getPlatformName(record.platform) }}</el-tag>
              <span>{{ getStatusText(record.status) }}</span><span>{{ getPublishTime(record) }}</span></div>
          </div>
          <div class="actions inline">
            <el-tag :type="getStatusType(record.status)" effect="plain">{{ getStatusText(record.status) }}</el-tag>
            <el-button link type="primary" @click="viewDetail(record)">详情</el-button>
            <el-button link type="danger" @click="deleteRecord(record.id)">删除</el-button>
          </div>
        </div>
      </div>
      <el-empty v-if="!loading && !filteredHistory.length" description="暂无发布记录"/>
      <el-pagination v-model:current-page="currentPage" v-model:page-size="pageSize" :total="total"
                     :page-sizes="[10,20,50,100]" layout="total, sizes, prev, pager, next" class="pagination"
                     @size-change="handleSizeChange" @current-change="handleCurrentChange"/>
    </el-card>

    <el-dialog v-model="showPublishDialog" title="新建发布" width="min(1120px,96vw)">
      <div class="dialog-layout">
        <div class="glass dialog-box">
          <el-form ref="publishFormRef" :model="publishForm" :rules="publishRules" label-position="top">
            <el-form-item label="选择内容" prop="creationId">
              <el-select v-model="publishForm.creationId" placeholder="请选择内容" style="width:100%"
                         @change="handleCreationChange">
                <el-option v-for="creation in creations" :key="creation.id" :label="creation.title"
                           :value="creation.id"/>
              </el-select>
            </el-form-item>
            <el-form-item label="发布账号" prop="accountId">
              <el-select v-model="publishForm.accountId" placeholder="请选择平台账号" style="width:100%">
                <el-option v-for="account in activeAccounts" :key="account.id"
                           :label="`${getPlatformName(account.platform)} · ${account.account_name}`"
                           :value="account.id"/>
              </el-select>
            </el-form-item>
            <el-form-item label="内容类型">
              <el-input v-model="publishForm.contentType"/>
            </el-form-item>
            <el-form-item label="发布时间" prop="publishType">
              <el-radio-group v-model="publishForm.publishType">
                <el-radio label="immediate">立即发布</el-radio>
                <el-radio label="scheduled">定时发布</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item v-if="publishForm.publishType === 'scheduled'" label="定时时间" prop="scheduledAt">
              <el-date-picker v-model="publishForm.scheduledAt" type="datetime" style="width:100%"
                              :disabled-date="disabledDate"/>
            </el-form-item>
            <el-form-item label="发布模板">
              <TemplateSelector v-model="publishForm.templateId" @change="handleTemplateChange"
                                @manage="goToTemplateManagement"/>
            </el-form-item>
          </el-form>
          <div class="foot">
            <el-button @click="showPublishDialog = false">取消</el-button>
            <el-button type="primary" :loading="publishing" @click="handlePublish">确认发布</el-button>
          </div>
        </div>
        <div class="glass dialog-box">
          <div class="preview-title">内容预览</div>
          <ContentPreview :content="contentPreview" :template="selectedTemplate"
                          :article-title="selectedCreation?.title || '内容预览'" :show-copy-button="true"
                          :is-markdown="true"/>
        </div>
      </div>
    </el-dialog>

    <el-dialog v-model="showBindDialog" title="绑定平台账号" width="min(720px,94vw)">
      <el-form ref="bindFormRef" :model="bindForm" :rules="bindRules" label-position="top">
        <div class="grid2">
          <el-form-item label="选择平台" prop="platformCode">
            <el-select v-model="bindForm.platformCode" placeholder="请选择平台" style="width:100%"
                       @change="handlePlatformChange">
              <el-option v-for="platform in platforms" :key="platform.platform" :label="platform.name"
                         :value="platform.platform"/>
            </el-select>
          </el-form-item>
          <el-form-item label="账号名称" prop="accountName">
            <el-input v-model="bindForm.accountName" placeholder="用于区分不同平台账号"/>
          </el-form-item>
        </div>
        <el-form-item label="授权方式">
          <el-radio-group v-model="bindForm.authMode">
<!--            <el-radio label="auto">自动授权</el-radio>-->
            <el-radio label="manual">手动填写 Cookie</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-alert v-if="loginInfo" type="info" :closable="false">
          <div class="login-info">登录入口：<a :href="loginInfo.login_url" target="_blank"
                                              rel="noreferrer">{{ loginInfo.login_url }}</a>
            <div>{{ loginInfo.instructions }}</div>
          </div>
        </el-alert>
        <el-form-item v-if="bindForm.authMode === 'manual'" label="Cookie 内容" prop="cookies">
          <el-input v-model="bindForm.cookies" type="textarea" :rows="7"
                    placeholder="支持 JSON 对象或标准 Cookie 字符串"/>
        </el-form-item>
        <div class="foot">
          <el-button @click="showBindDialog = false">取消</el-button>
          <el-button v-if="loginInfo" @click="openLoginPage">打开登录页</el-button>
          <el-button type="primary" :loading="binding" @click="handleBind">
            {{ bindForm.authMode === 'auto' ? '开始授权' : '确认绑定' }}
          </el-button>
        </div>
      </el-form>
    </el-dialog>

    <el-dialog v-model="showCookieDialog" title="更新 Cookie" width="min(680px,94vw)">
      <el-form ref="cookieFormRef" :model="cookieForm" :rules="cookieRules" label-position="top">
        <el-form-item label="当前账号">
          <el-input :model-value="cookieForm.accountLabel" disabled/>
        </el-form-item>
        <el-form-item label="Cookie 内容" prop="cookies">
          <el-input v-model="cookieForm.cookies" type="textarea" :rows="8"
                    placeholder="支持 JSON 对象或标准 Cookie 字符串"/>
        </el-form-item>
        <div class="foot">
          <el-button @click="showCookieDialog = false">取消</el-button>
          <el-button type="primary" :loading="updatingCookies" @click="handleUpdateCookies">保存更新</el-button>
        </div>
      </el-form>
    </el-dialog>

    <el-dialog v-model="showDetailDialog" title="发布详情" width="min(960px,96vw)">
      <div v-if="currentRecord" class="detail-layout">
        <div class="glass dialog-box">
          <div class="meta"><span>标题</span><strong>{{ currentRecord.title || '未命名内容' }}</strong></div>
          <div class="meta"><span>平台</span><strong>{{ getPlatformName(currentRecord.platform) }}</strong></div>
          <div class="meta"><span>状态</span>
            <el-tag :type="getStatusType(currentRecord.status)">{{ getStatusText(currentRecord.status) }}</el-tag>
          </div>
          <div class="meta"><span>账号</span><strong>{{ currentRecord.account_name || '-' }}</strong></div>
          <div class="meta"><span>发布时间</span><strong>{{ getPublishTime(currentRecord) }}</strong></div>
          <div v-if="currentRecord.platform_url" class="meta"><span>平台链接</span><a class="plink"
                                                                                      :href="currentRecord.platform_url"
                                                                                      target="_blank" rel="noreferrer">打开原文</a>
          </div>
          <div v-if="currentRecord.error_message" class="err">{{ currentRecord.error_message }}</div>
        </div>
        <div class="glass dialog-box">
          <div class="preview-title">渲染内容</div>
          <el-button v-if="currentRecord.rendered_content" link type="primary" @click="copyRenderedContent">复制 HTML
          </el-button>
          <div class="rendered"
               v-html="currentRecord.rendered_content || currentRecord.content || '<p>暂无内容</p>'"></div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import {computed, onMounted, reactive, ref} from 'vue'
import {useRouter} from 'vue-router'
import {ElMessage, ElMessageBox} from 'element-plus'
import {Search, Upload} from '@element-plus/icons-vue'
import type {FormInstance, FormRules} from 'element-plus'
import TemplateSelector from '@/components/TemplateSelector.vue'
import ContentPreview from '@/components/ContentPreview.vue'
import type {ArticleTemplate} from '@/types/template'
import {renderForWechat} from '@/services/markdownRenderer'
import type {Creation, Platform, PlatformAccount, PublishRecord} from '@/types'
import {
  authorizePlatformAccount,
  createPlatformAccount,
  deletePlatformAccount,
  deletePublishRecord,
  getPlatformAccounts,
  getPlatformLoginInfo,
  getPlatforms,
  getPublishHistory,
  getPublishHistoryDetail,
  publishContent,
  updatePlatformCookies,
  validatePlatformCookies
} from '@/api/publish'
import {getCreations} from '@/api/creations'

const router = useRouter()
const loading = ref(false), publishing = ref(false), binding = ref(false), updatingCookies = ref(false),
    loadingAccounts = ref(false)
const showPublishDialog = ref(false), showBindDialog = ref(false), showCookieDialog = ref(false),
    showDetailDialog = ref(false)
const searchKeyword = ref(''), currentPage = ref(1), pageSize = ref(10), total = ref(0)
const loginInfo = ref<{ platform: string; name: string; login_url: string; instructions: string } | null>(null)
const platforms = ref<Platform[]>([]), platformAccounts = ref<PlatformAccount[]>([]),
    publishHistory = ref<PublishRecord[]>([]), creations = ref<Creation[]>([])
const currentRecord = ref<PublishRecord | null>(null), selectedCreation = ref<Creation | null>(null),
    selectedTemplate = ref<ArticleTemplate | null>(null), contentPreview = ref('')
const publishFormRef = ref<FormInstance>(), bindFormRef = ref<FormInstance>(), cookieFormRef = ref<FormInstance>()
const publishForm = reactive({
  creationId: undefined as number | undefined,
  accountId: undefined as number | undefined,
  contentType: '',
  publishType: 'immediate',
  scheduledAt: null as Date | null,
  templateId: undefined as number | undefined
})
const bindForm = reactive({platformCode: '', accountName: '', cookies: '', authMode: 'manual'})
const cookieForm = reactive({accountId: 0, accountLabel: '', cookies: ''})
const publishRules: FormRules = {
  creationId: [{required: true, message: '请选择需要发布的内容', trigger: 'change'}],
  accountId: [{required: true, message: '请选择平台账号', trigger: 'change'}],
  scheduledAt: [{
    validator: (_r, v, cb) => {
      if (publishForm.publishType === 'scheduled' && !v) return cb(new Error('请选择定时发布时间'));
      cb()
    }, trigger: 'change'
  }]
}
const bindRules: FormRules = {
  platformCode: [{required: true, message: '请选择平台', trigger: 'change'}],
  accountName: [{required: true, message: '请输入账号名称', trigger: 'blur'}],
  cookies: [{
    validator: (_r, v, cb) => {
      if (bindForm.authMode === 'manual' && !v) return cb(new Error('请输入 Cookie'));
      cb()
    }, trigger: 'blur'
  }]
}
const cookieRules: FormRules = {cookies: [{required: true, message: '请输入 Cookie', trigger: 'blur'}]}
const activeAccounts = computed(() => platformAccounts.value.filter((i) => i.is_active === 'active'))
const filteredHistory = computed(() => {
  const k = searchKeyword.value.trim().toLowerCase();
  return k ? publishHistory.value.filter((i) => (i.title || '').toLowerCase().includes(k) || getPlatformName(i.platform).toLowerCase().includes(k)) : publishHistory.value
})
const getPlatformName = (code: string) => platforms.value.find((i) => i.platform === code)?.name || code
const getStatusType = (s: string) => ({
  draft: 'info',
  pending: 'warning',
  publishing: 'warning',
  success: 'success',
  failed: 'danger',
  scheduled: 'info'
}[s] || 'info')
const getStatusText = (s: string) => ({
  draft: '草稿',
  pending: '待发布',
  publishing: '发布中',
  success: '已发布',
  failed: '发布失败',
  scheduled: '已定时'
}[s] || '未知状态')
const getCookieStatusType = (s?: string | null) => s === 'valid' ? 'success' : s === 'invalid' ? 'danger' : 'info'
const getCookieStatusText = (s?: string | null) => s === 'valid' ? '有效' : s === 'invalid' ? '失效' : '未校验'
const formatDate = (d: string) => new Date(d).toLocaleString('zh-CN', {
  year: 'numeric',
  month: '2-digit',
  day: '2-digit',
  hour: '2-digit',
  minute: '2-digit'
})
const getPublishTime = (r: PublishRecord) => formatDate((r.status === 'scheduled' && r.scheduled_at) ? r.scheduled_at : (r.published_at || r.created_at) as string)
const disabledDate = (time: Date) => time.getTime() < Date.now() - 60000
const parseCookieString = (s: string) => {
  const cookies: Record<string, string> = {};
  s.split(';').forEach((p) => {
    const [n, ...rest] = p.split('=');
    if (n && rest.length) cookies[n.trim()] = rest.join('=').trim()
  });
  return cookies
}
const loadPlatforms = async () => {
  try {
    platforms.value = await getPlatforms() || []
  } catch (e: any) {
    ElMessage.error(e.message || '加载平台列表失败')
  }
}
const loadPlatformAccounts = async () => {
  loadingAccounts.value = true;
  try {
    platformAccounts.value = await getPlatformAccounts() || []
  } catch (e: any) {
    ElMessage.error(e.message || '加载平台账号失败')
  } finally {
    loadingAccounts.value = false
  }
}
const loadPublishHistory = async () => {
  loading.value = true;
  try {
    const r = await getPublishHistory({skip: (currentPage.value - 1) * pageSize.value, limit: pageSize.value});
    publishHistory.value = r.items || [];
    total.value = r.total || 0
  } catch (e: any) {
    ElMessage.error(e.message || '加载发布记录失败')
  } finally {
    loading.value = false
  }
}
const loadCreations = async () => {
  try {
    const r = await getCreations({page: 1, page_size: 100});
    creations.value = r.items || []
  } catch (e: any) {
    ElMessage.error(e.message || '加载创作列表失败')
  }
}
const handleSizeChange = (s: number) => {
  pageSize.value = s;
  loadPublishHistory()
}
const handleCurrentChange = (p: number) => {
  currentPage.value = p;
  loadPublishHistory()
}
const handleCreationChange = (id: number) => {
  const c = creations.value.find((i) => i.id === id) || null;
  selectedCreation.value = c;
  contentPreview.value = c?.output_content || c?.content || '';
  publishForm.contentType = c?.content_type || c?.creation_type || 'article'
}
const handleTemplateChange = (t: ArticleTemplate) => {
  selectedTemplate.value = t
}
const goToTemplateManagement = () => {
  showPublishDialog.value = false;
  router.push('/templates')
}
const handlePublish = async () => {
  if (!publishFormRef.value || !selectedCreation.value) return;
  await publishFormRef.value.validate(async (valid) => {
    if (!valid) return;
    publishing.value = true;
    try {
      const raw = selectedCreation.value?.output_content || selectedCreation.value?.content || '';
      await publishContent({
        account_id: publishForm.accountId!,
        creation_id: publishForm.creationId!,
        content_type: publishForm.contentType,
        scheduled_at: publishForm.publishType === 'scheduled' && publishForm.scheduledAt ? publishForm.scheduledAt.toISOString() : undefined,
        title: selectedCreation.value.title,
        content: raw,
        rendered_content: renderForWechat(raw, selectedTemplate.value),
        template_id: publishForm.templateId
      });
      ElMessage.success('发布任务已创建');
      showPublishDialog.value = false;
      loadPublishHistory()
    } catch (e: any) {
      ElMessage.error(e.message || '发布失败')
    } finally {
      publishing.value = false
    }
  })
}
const openBindDialog = () => {
  bindForm.platformCode = '';
  bindForm.accountName = '';
  bindForm.cookies = '';
  bindForm.authMode = 'manual';
  loginInfo.value = null;
  showBindDialog.value = true
}
const openBindDialogWithPreselect = (a: PlatformAccount) => {
  bindForm.platformCode = a.platform;
  bindForm.accountName = a.account_name;
  bindForm.cookies = '';
  bindForm.authMode = 'manual';
  showBindDialog.value = true;
  handlePlatformChange(a.platform)
}
const openCookieDialog = (a: PlatformAccount) => {
  cookieForm.accountId = a.id;
  cookieForm.accountLabel = `${getPlatformName(a.platform)} · ${a.account_name}`;
  cookieForm.cookies = '';
  showCookieDialog.value = true
}
const openLoginPage = () => {
  if (!loginInfo.value?.login_url) return ElMessage.warning('当前平台没有可用的登录地址');
  window.open(loginInfo.value.login_url, '_blank')
}
const handlePlatformChange = async (code: string) => {
  if (!code) return;
  try {
    loginInfo.value = await getPlatformLoginInfo(code)
  } catch (e: any) {
    loginInfo.value = null;
    ElMessage.error(e.message || '获取平台登录信息失败')
  }
}
const handleBind = async () => {
  if (!bindFormRef.value) return;
  await bindFormRef.value.validate(async (valid) => {
    if (!valid) return;
    binding.value = true;
    try {
      if (bindForm.authMode === 'auto') {
        await authorizePlatformAccount({platform: bindForm.platformCode, account_name: bindForm.accountName});
        ElMessage.success('授权成功，已自动获取 Cookie')
      } else {
        let cookies: Record<string, string> = {};
        try {
          cookies = JSON.parse(bindForm.cookies)
        } catch {
          cookies = parseCookieString(bindForm.cookies)
        }
        if (!Object.keys(cookies).length) return ElMessage.error('Cookie 格式错误');
        const account = await createPlatformAccount({
          platform: bindForm.platformCode,
          account_name: bindForm.accountName
        });
        const r = await updatePlatformCookies(account.id, cookies);
        r.valid ? ElMessage.success('平台账号绑定成功') : ElMessage.warning(r.message || '账号已绑定，但 Cookie 校验失败')
      }
      showBindDialog.value = false;
      await loadPlatformAccounts()
    } catch (e: any) {
      ElMessage.error(e.message || '绑定账号失败')
    } finally {
      binding.value = false
    }
  })
}
const handleUpdateCookies = async () => {
  if (!cookieFormRef.value) return;
  await cookieFormRef.value.validate(async (valid) => {
    if (!valid) return;
    updatingCookies.value = true;
    try {
      let cookies: Record<string, string> = {};
      try {
        cookies = JSON.parse(cookieForm.cookies)
      } catch {
        cookies = parseCookieString(cookieForm.cookies)
      }
      if (!Object.keys(cookies).length) return ElMessage.error('Cookie 格式错误');
      const r = await updatePlatformCookies(cookieForm.accountId, cookies);
      r.valid ? ElMessage.success('Cookie 更新成功') : ElMessage.warning(r.message || 'Cookie 更新失败');
      showCookieDialog.value = false;
      loadPlatformAccounts()
    } catch (e: any) {
      ElMessage.error(e.message || '更新 Cookie 失败')
    } finally {
      updatingCookies.value = false
    }
  })
}
const handleValidateCookies = async (a: PlatformAccount) => {
  try {
    const r = await validatePlatformCookies(a.id);
    r.valid ? ElMessage.success('Cookie 校验通过') : ElMessage.warning(r.message || 'Cookie 已失效');
    loadPlatformAccounts()
  } catch (e: any) {
    ElMessage.error(e.message || '验证 Cookie 失败')
  }
}
const unbindPlatform = async (id: number) => {
  try {
    await ElMessageBox.confirm('确认删除该平台账号吗？', '提示', {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
      type: 'warning'
    });
    await deletePlatformAccount(id);
    ElMessage.success('平台账号已删除');
    loadPlatformAccounts()
  } catch (e: any) {
    if (e !== 'cancel') ElMessage.error(e.message || '删除平台账号失败')
  }
}
const viewDetail = async (r: PublishRecord) => {
  try {
    currentRecord.value = await getPublishHistoryDetail(r.id)
  } catch {
    currentRecord.value = r
  } finally {
    showDetailDialog.value = true
  }
}
const copyRenderedContent = async () => {
  if (!currentRecord.value?.rendered_content) return ElMessage.warning('当前记录没有可复制的 HTML');
  try {
    await navigator.clipboard.writeText(currentRecord.value.rendered_content);
    ElMessage.success('HTML 已复制到剪贴板')
  } catch {
    ElMessage.error('复制失败，请手动复制')
  }
}
const deleteRecord = async (id: number) => {
  try {
    await ElMessageBox.confirm('确认删除该发布记录吗？', '提示', {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
      type: 'warning'
    });
    await deletePublishRecord(id);
    ElMessage.success('发布记录已删除');
    loadPublishHistory()
  } catch (e: any) {
    if (e !== 'cancel') ElMessage.error(e.message || '删除发布记录失败')
  }
}
onMounted(() => {
  loadPlatforms();
  loadPlatformAccounts();
  loadPublishHistory();
  loadCreations()
})
</script>
<style scoped lang="scss">
.publish-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding: 28px
}

.hero {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 20px;
  padding: 30px;
  border: 1px solid rgba(148, 163, 184, .2);
  border-radius: 30px;
  background: radial-gradient(circle at top right, rgba(125, 211, 252, .38), transparent 28%), linear-gradient(135deg, rgba(239, 246, 255, .94), rgba(255, 255, 255, .92));
  box-shadow: 0 24px 60px rgba(15, 23, 42, .08)
}

.eyebrow {
  margin: 0 0 10px;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: .2em;
  text-transform: uppercase;
  color: #2563eb
}

.hero h1 {
  margin: 0;
  font-size: clamp(30px, 4vw, 42px);
  color: #12304a
}

.desc {
  margin: 14px 0 0;
  font-size: 15px;
  line-height: 1.75;
  color: #60758e
}

.hero-actions, .toolbar, .actions, .foot {
  display: flex;
  align-items: center;
  gap: 12px
}

.stats {
  display: grid;
  grid-template-columns:repeat(3, minmax(0, 1fr));
  gap: 18px
}

.glass {
  border: 1px solid rgba(148, 163, 184, .2);
  border-radius: 26px;
  background: rgba(255, 255, 255, .9);
  box-shadow: 0 20px 44px rgba(15, 23, 42, .07)
}

.label {
  font-size: 13px;
  color: #6b7280
}

.value {
  margin-top: 12px;
  font-size: 34px;
  font-weight: 700;
  color: #12304a
}

.panel :deep(.el-card__header) {
  padding-bottom: 0;
  border-bottom: 0
}

.panel-head {
  display: flex;
  justify-content: space-between;
  gap: 16px
}

.panel-head h3 {
  margin: 0;
  font-size: 20px;
  color: #12304a
}

.panel-head p {
  margin: 8px 0 0;
  font-size: 14px;
  color: #62748a
}

.panel-head-row {
  align-items: center
}

.search {
  width: 260px
}

.account-grid, .dialog-layout, .detail-layout {
  display: grid;
  grid-template-columns:repeat(2, minmax(0, 1fr));
  gap: 18px
}

.account-card, .dialog-box {
  padding: 20px;
  border: 1px solid rgba(148, 163, 184, .18);
  border-radius: 22px;
  background: linear-gradient(180deg, rgba(248, 250, 252, .96), rgba(239, 246, 255, .82))
}

.row, .meta, .history-item {
  display: flex;
  justify-content: space-between;
  gap: 12px
}

.top strong, .history-item strong {
  display: block;
  font-size: 18px;
  color: #12304a
}

.top span {
  display: block;
  margin-top: 6px;
  font-size: 14px;
  color: #62748a
}

.meta {
  margin-top: 12px;
  align-items: center;
  font-size: 13px;
  color: #526579
}

.actions {
  flex-wrap: wrap;
  margin-top: 16px
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 14px
}

.history-item {
  padding: 18px 20px;
  border: 1px solid rgba(148, 163, 184, .18);
  border-radius: 22px;
  background: linear-gradient(180deg, rgba(255, 255, 255, .92), rgba(248, 250, 252, .9));
  align-items: center
}

.sub {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 10px;
  font-size: 13px;
  color: #66788a
}

.inline {
  margin-top: 0;
  align-items: center
}

.pagination {
  margin-top: 18px;
  justify-content: flex-end
}

.preview-title {
  margin-bottom: 14px;
  font-size: 16px;
  font-weight: 700;
  color: #12304a
}

.grid2 {
  display: grid;
  grid-template-columns:repeat(2, minmax(0, 1fr));
  gap: 16px
}

.login-info {
  line-height: 1.7
}

.login-info a, .plink {
  color: #2563eb;
  text-decoration: none
}

.err {
  margin-top: 14px;
  padding: 12px 14px;
  border-radius: 16px;
  color: #b91c1c;
  background: rgba(254, 226, 226, .86)
}

.rendered {
  max-height: 640px;
  overflow: auto;
  margin-top: 12px;
  padding: 18px;
  border-radius: 18px;
  background: #fff;
  border: 1px solid rgba(148, 163, 184, .16);
  line-height: 1.8
}

.rendered :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 12px
}

.rendered :deep(pre) {
  overflow: auto;
  padding: 14px;
  border-radius: 14px;
  background: #0f172a;
  color: #e2e8f0
}

@media (max-width: 1080px) {
  .stats, .account-grid, .dialog-layout, .detail-layout {
    grid-template-columns:1fr
  }
}

@media (max-width: 768px) {
  .publish-page {
    padding: 16px
  }
  .hero, .panel-head-row, .history-item, .hero-actions, .toolbar, .foot {
    flex-direction: column;
    align-items: stretch
  }
  .stats, .grid2 {
    grid-template-columns:1fr
  }
  .search {
    width: 100%
  }
  .inline {
    justify-content: space-between
  }
  .pagination {
    justify-content: center
  }
}
</style>
