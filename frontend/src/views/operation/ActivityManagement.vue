<template>
  <div class="activity-management flagship-page page-shell">
    <section class="page-hero activity-hero">
      <div class="hero-grid">
        <div class="hero-main">
          <span class="hero-eyebrow">Campaigns</span>
          <h1 class="hero-title">活动管理</h1>
          <p class="hero-subtitle">创建与管理运营活动，提升用户活跃度。</p>
          <div class="hero-actions">
            <el-button type="primary" @click="showCreateDialog">创建活动</el-button>
            <el-button @click="loadActivities">刷新列表</el-button>
          </div>
        </div>
        <div class="hero-panel">
          <div class="hero-panel-title">活动概览</div>
          <div class="hero-stats">
            <div class="hero-stat">
              <div class="hero-stat-value">{{ pagination.total }}</div>
              <div class="hero-stat-label">活动数量</div>
            </div>
            <div class="hero-stat">
              <div class="hero-stat-value">{{ activities.length }}</div>
              <div class="hero-stat-label">当前列表</div>
            </div>
            <div class="hero-stat">
              <div class="hero-stat-value">{{ searchForm.activity_type || '全部' }}</div>
              <div class="hero-stat-label">类型筛选</div>
            </div>
            <div class="hero-stat">
              <div class="hero-stat-value">{{ searchForm.status || '全部' }}</div>
              <div class="hero-stat-label">状态筛选</div>
            </div>
          </div>
          <div class="hero-tags">
            <span class="hero-tag">积分赠送</span>
            <span class="hero-tag">充值优惠</span>
            <span class="hero-tag">会员优惠</span>
          </div>
        </div>
      </div>
    </section>

    <section class="page-dashboard">
      <div class="dashboard-grid">
        <div class="dashboard-card">
          <div class="label">活动总量</div>
          <div class="value">{{ pagination.total }}</div>
          <div class="delta">支持多种活动类型</div>
        </div>
        <div class="dashboard-card">
          <div class="label">筛选类型</div>
          <div class="value">{{ searchForm.activity_type || '全部' }}</div>
          <div class="delta">按需筛选活动</div>
        </div>
        <div class="dashboard-card">
          <div class="label">筛选状态</div>
          <div class="value">{{ searchForm.status || '全部' }}</div>
          <div class="delta">实时查看活动进展</div>
        </div>
      </div>
    </section>

    <section class="page-body">
      <div class="main-panel">
        <el-card>
      <template #header>
        <div class="card-header">
          <span>活动管理</span>
          <el-button type="primary" @click="showCreateDialog">创建活动</el-button>
        </div>
      </template>

      <el-form :inline="true" :model="searchForm">
        <el-form-item label="活动类型">
          <el-select v-model="searchForm.activity_type" placeholder="全部" clearable>
            <el-option label="积分赠送" value="credit_gift" />
            <el-option label="充值优惠" value="recharge_discount" />
            <el-option label="会员优惠" value="membership_discount" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="全部" clearable>
            <el-option label="草稿" value="draft" />
            <el-option label="进行中" value="active" />
            <el-option label="已结束" value="ended" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadActivities">查询</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="activities" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="活动标题" />
        <el-table-column prop="activity_type" label="活动类型">
          <template #default="{ row }">
            <el-tag v-if="row.activity_type === 'credit_gift'">积分赠送</el-tag>
            <el-tag v-else-if="row.activity_type === 'recharge_discount'" type="success">充值优惠</el-tag>
            <el-tag v-else-if="row.activity_type === 'membership_discount'" type="warning">会员优惠</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="reward_amount" label="奖励金额" />
        <el-table-column prop="current_participants" label="参与人数" />
        <el-table-column prop="status" label="状态">
          <template #default="{ row }">
            <el-tag v-if="row.status === 'draft'" type="info">草稿</el-tag>
            <el-tag v-else-if="row.status === 'active'" type="success">进行中</el-tag>
            <el-tag v-else type="danger">已结束</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button size="small" @click="viewActivity(row)">查看</el-button>
            <el-button size="small" type="primary" @click="editActivity(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteActivity(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        layout="total, prev, pager, next"
        @current-change="loadActivities"
      />
        </el-card>
      </div>
      <aside class="side-panel">
        <div class="panel">
          <h3 class="panel-title">运营建议</h3>
          <p class="panel-subtitle">活动规则清晰可提升参与率</p>
          <div class="info-list">
            <div class="info-item">
              <div class="info-title">活动类型</div>
              <div class="info-desc">针对不同用户群设置不同激励。</div>
            </div>
            <div class="info-item">
              <div class="info-title">奖励设置</div>
              <div class="info-desc">奖励需与目标行为匹配。</div>
            </div>
          </div>
        </div>
        <div class="panel">
          <h3 class="panel-title">筛选状态</h3>
          <div class="info-list">
            <div class="info-item">
              <div class="info-title">类型</div>
              <div class="info-desc">{{ searchForm.activity_type || '全部' }}</div>
            </div>
            <div class="info-item">
              <div class="info-title">状态</div>
              <div class="info-desc">{{ searchForm.status || '全部' }}</div>
            </div>
          </div>
        </div>
      </aside>
    </section>

    <!-- 创建/编辑活动对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
    >
      <el-form :model="activityForm" label-width="100px">
        <el-form-item label="活动标题" required>
          <el-input v-model="activityForm.title" />
        </el-form-item>
        <el-form-item label="活动描述" required>
          <el-input v-model="activityForm.description" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="活动类型" required>
          <el-select v-model="activityForm.activity_type">
            <el-option label="积分赠送" value="credit_gift" />
            <el-option label="充值优惠" value="recharge_discount" />
            <el-option label="会员优惠" value="membership_discount" />
          </el-select>
        </el-form-item>
        <el-form-item label="奖励类型" required>
          <el-select v-model="activityForm.reward_type">
            <el-option label="积分" value="credit" />
            <el-option label="优惠券" value="coupon" />
          </el-select>
        </el-form-item>
        <el-form-item label="奖励金额" required>
          <el-input-number v-model="activityForm.reward_amount" :min="0" />
        </el-form-item>
        <el-form-item label="开始时间" required>
          <el-date-picker
            v-model="activityForm.start_time"
            type="datetime"
            placeholder="选择开始时间"
          />
        </el-form-item>
        <el-form-item label="结束时间" required>
          <el-date-picker
            v-model="activityForm.end_time"
            type="datetime"
            placeholder="选择结束时间"
          />
        </el-form-item>
        <el-form-item label="参与人数限制">
          <el-input-number v-model="activityForm.max_participants" :min="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveActivity">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as operationApi from '@/api/operation'

const activities = ref<operationApi.Activity[]>([])
const searchForm = reactive({
  activity_type: '',
  status: '',
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0,
})

const dialogVisible = ref(false)
const dialogTitle = ref('创建活动')
const activityForm = reactive({
  id: 0,
  title: '',
  description: '',
  activity_type: 'credit_gift',
  reward_type: 'credit',
  reward_amount: 0,
  start_time: '',
  end_time: '',
  max_participants: undefined as number | undefined,
})

const loadActivities = async () => {
  try {
    const params = {
      skip: (pagination.page - 1) * pagination.pageSize,
      limit: pagination.pageSize,
      ...searchForm,
    }
    const response = await operationApi.getActivities(params)
    activities.value = response.data
    pagination.total = response.data.length
  } catch (error) {
    ElMessage.error('加载活动列表失败')
  }
}

const showCreateDialog = () => {
  dialogTitle.value = '创建活动'
  resetForm()
  dialogVisible.value = true
}

const viewActivity = (activity: operationApi.Activity) => {
  ElMessageBox.alert(
    `<p><strong>活动标题：</strong>${activity.title}</p>
     <p><strong>活动描述：</strong>${activity.description}</p>
     <p><strong>奖励金额：</strong>${activity.reward_amount}</p>
     <p><strong>参与人数：</strong>${activity.current_participants}</p>`,
    '活动详情',
    {
      dangerouslyUseHTMLString: true,
    }
  )
}

const editActivity = (activity: operationApi.Activity) => {
  dialogTitle.value = '编辑活动'
  Object.assign(activityForm, activity)
  dialogVisible.value = true
}

const deleteActivity = async (activity: operationApi.Activity) => {
  try {
    await ElMessageBox.confirm('确定要删除这个活动吗？', '提示', {
      type: 'warning',
    })
    await operationApi.deleteActivity(activity.id)
    ElMessage.success('删除成功')
    loadActivities()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const saveActivity = async () => {
  try {
    if (activityForm.id) {
      await operationApi.updateActivity(activityForm.id, activityForm)
      ElMessage.success('更新成功')
    } else {
      await operationApi.createActivity(activityForm)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadActivities()
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const resetForm = () => {
  activityForm.id = 0
  activityForm.title = ''
  activityForm.description = ''
  activityForm.activity_type = 'credit_gift'
  activityForm.reward_type = 'credit'
  activityForm.reward_amount = 0
  activityForm.start_time = ''
  activityForm.end_time = ''
  activityForm.max_participants = undefined
}

onMounted(() => {
  loadActivities()
})
</script>

<style scoped>
.activity-management {
  padding: 20px;
  --hero-from: rgba(59, 130, 246, 0.18);
  --hero-to: rgba(14, 165, 233, 0.18);
  --page-accent: #2563eb;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.el-pagination {
  margin-top: 20px;
  justify-content: center;
}
</style>

