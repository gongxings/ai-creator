<template>
  <div class="referral-management flagship-page page-shell">
    <section class="page-hero referral-hero">
      <div class="hero-grid">
        <div class="hero-main">
          <span class="hero-eyebrow">Referral</span>
          <h1 class="hero-title">推广管理</h1>
          <p class="hero-subtitle">管理你的推广链接与返利记录。</p>
          <div class="hero-actions">
            <el-button type="primary" @click="copyReferralCode">复制推荐码</el-button>
            <el-button @click="copyReferralLink">复制链接</el-button>
          </div>
        </div>
        <div class="hero-panel">
          <div class="hero-panel-title">推广概览</div>
          <div class="hero-stats">
            <div class="hero-stat">
              <div class="hero-stat-value">{{ statistics.total_referrals }}</div>
              <div class="hero-stat-label">累计推广</div>
            </div>
            <div class="hero-stat">
              <div class="hero-stat-value">{{ statistics.total_rewards }}</div>
              <div class="hero-stat-label">累计返利</div>
            </div>
            <div class="hero-stat">
              <div class="hero-stat-value">{{ statistics.pending_rewards }}</div>
              <div class="hero-stat-label">待发放</div>
            </div>
            <div class="hero-stat">
              <div class="hero-stat-value">{{ pagination.total }}</div>
              <div class="hero-stat-label">记录数</div>
            </div>
          </div>
          <div class="hero-tags">
            <span class="hero-tag">注册返利</span>
            <span class="hero-tag">充值返利</span>
            <span class="hero-tag">会员返利</span>
          </div>
        </div>
      </div>
    </section>

    <section class="page-dashboard">
      <div class="dashboard-grid">
        <div class="dashboard-card">
          <div class="label">累计推广</div>
          <div class="value">{{ statistics.total_referrals }}</div>
          <div class="delta">推荐用户增长</div>
        </div>
        <div class="dashboard-card">
          <div class="label">累计返利</div>
          <div class="value">{{ statistics.total_rewards }}</div>
          <div class="delta">积分奖励已累计</div>
        </div>
        <div class="dashboard-card">
          <div class="label">待发放</div>
          <div class="value">{{ statistics.pending_rewards }}</div>
          <div class="delta">预计尽快发放</div>
        </div>
      </div>
    </section>

    <section class="page-body">
      <div class="main-panel">
        <el-row :gutter="20">
      <el-col :span="24">
        <el-card>
          <template #header>
            <span>我的推广</span>
          </template>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="推荐码">
              <el-tag type="success" size="large">{{ statistics.referral_code }}</el-tag>
              <el-button size="small" @click="copyReferralCode" style="margin-left: 10px">复制</el-button>
            </el-descriptions-item>
            <el-descriptions-item label="推广链接">
              <el-input v-model="referralLink" readonly>
                <template #append>
                  <el-button @click="copyReferralLink">复制</el-button>
                </template>
              </el-input>
            </el-descriptions-item>
            <el-descriptions-item label="累计推广人数">
              {{ statistics.total_referrals }}
            </el-descriptions-item>
            <el-descriptions-item label="累计返利金额">
              {{ statistics.total_rewards }} 积分
            </el-descriptions-item>
            <el-descriptions-item label="待发放返利">
              {{ statistics.pending_rewards }} 积分
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
        </el-row>

        <el-card style="margin-top: 20px">
      <template #header>
        <span>推广记录</span>
      </template>

      <el-form :inline="true" :model="searchForm">
        <el-form-item label="返利状态">
          <el-select v-model="searchForm.status" placeholder="全部" clearable>
            <el-option label="待发放" value="pending" />
            <el-option label="已发放" value="rewarded" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadRecords">查询</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="records" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="referred_id" label="被推荐用户ID" />
        <el-table-column prop="referral_type" label="推广类型">
          <template #default="{ row }">
            <el-tag v-if="row.referral_type === 'register'">注册</el-tag>
            <el-tag v-else-if="row.referral_type === 'recharge'" type="success">充值</el-tag>
            <el-tag v-else type="warning">会员</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="reward_amount" label="返利金额">
          <template #default="{ row }">
            {{ row.reward_amount }} 积分
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态">
          <template #default="{ row }">
            <el-tag v-if="row.status === 'pending'" type="warning">待发放</el-tag>
            <el-tag v-else-if="row.status === 'rewarded'" type="success">已发放</el-tag>
            <el-tag v-else type="danger">已取消</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="推广时间" />
        <el-table-column prop="rewarded_at" label="发放时间" />
      </el-table>

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        layout="total, prev, pager, next"
        @current-change="loadRecords"
      />
        </el-card>
      </div>
      <aside class="side-panel">
        <div class="panel">
          <h3 class="panel-title">推广建议</h3>
          <p class="panel-subtitle">分享链接可获取积分奖励</p>
          <div class="info-list">
            <div class="info-item">
              <div class="info-title">分享渠道</div>
              <div class="info-desc">社群、朋友圈与公众号效果更佳。</div>
            </div>
            <div class="info-item">
              <div class="info-title">激励引导</div>
              <div class="info-desc">强调新用户可享受创作福利。</div>
            </div>
          </div>
        </div>
        <div class="panel">
          <h3 class="panel-title">当前链接</h3>
          <div class="info-list">
            <div class="info-item">
              <div class="info-title">推荐码</div>
              <div class="info-desc">{{ statistics.referral_code || '-' }}</div>
            </div>
            <div class="info-item">
              <div class="info-title">推广链接</div>
              <div class="info-desc">{{ referralLink }}</div>
            </div>
          </div>
        </div>
      </aside>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import * as operationApi from '@/api/operation'

const statistics = ref<operationApi.ReferralStatistics>({
  total_referrals: 0,
  total_rewards: 0,
  pending_rewards: 0,
  referral_code: '',
})

const records = ref<operationApi.ReferralRecord[]>([])
const searchForm = reactive({
  status: '',
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0,
})

const referralLink = computed(() => {
  return `${window.location.origin}/register?ref=${statistics.value.referral_code}`
})

const loadStatistics = async () => {
  try {
    const response = await operationApi.getReferralStatistics()
    statistics.value = response.data
  } catch (error) {
    ElMessage.error('加载推广统计失败')
  }
}

const loadRecords = async () => {
  try {
    const params = {
      skip: (pagination.page - 1) * pagination.pageSize,
      limit: pagination.pageSize,
      ...searchForm,
    }
    const response = await operationApi.getReferralRecords(params)
    records.value = response.data
    pagination.total = response.data.length
  } catch (error) {
    ElMessage.error('加载推广记录失败')
  }
}

const copyReferralCode = () => {
  navigator.clipboard.writeText(statistics.value.referral_code)
  ElMessage.success('推荐码已复制')
}

const copyReferralLink = () => {
  navigator.clipboard.writeText(referralLink.value)
  ElMessage.success('推广链接已复制')
}

onMounted(() => {
  loadStatistics()
  loadRecords()
})
</script>

<style scoped>
.referral-management {
  padding: 20px;
  --hero-from: rgba(59, 130, 246, 0.18);
  --hero-to: rgba(14, 165, 233, 0.18);
  --page-accent: #2563eb;
}

.el-pagination {
  margin-top: 20px;
  justify-content: center;
}
</style>

