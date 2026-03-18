<template>
  <div class="transaction-history page-shell">
    <section class="page-hero">
      <div>
        <p class="eyebrow">Transactions</p>
        <h1>交易记录</h1>
        <p class="description">集中查看积分变化、账户余额和关联订单，方便快速追溯充值与消耗情况。</p>
      </div>
    </section>

    <el-card class="balance-card glass-card">
      <div class="balance-info">
        <div class="balance-main">
          <div class="balance-item">
            <span class="label">当前积分</span>
            <span class="value">{{ balance.credits }}</span>
          </div>
          <div class="balance-item">
            <span class="label">会员状态</span>
            <span class="value">
              <el-tag v-if="balance.is_member" type="success" effect="dark">会员</el-tag>
              <el-tag v-else type="info">普通用户</el-tag>
            </span>
          </div>
          <div v-if="balance.is_member && balance.member_expired_at" class="balance-item">
            <span class="label">到期时间</span>
            <span class="value date">{{ formatDate(balance.member_expired_at) }}</span>
          </div>
        </div>
        <div class="balance-actions">
          <el-button type="primary" @click="router.push('/credit/recharge')">
            <el-icon><Wallet /></el-icon>
            立即充值
          </el-button>
          <el-button @click="router.push('/credit/membership')">
            <el-icon><Medal /></el-icon>
            购买会员
          </el-button>
        </div>
      </div>
    </el-card>

    <el-card class="glass-card">
      <template #header>
        <div class="card-header">
          <span>交易记录</span>
          <el-button type="primary" @click="loadTransactions">刷新</el-button>
        </div>
      </template>

      <el-form :inline="true" :model="filters" class="filter-form">
        <el-form-item label="交易类型">
          <el-select v-model="filters.type" placeholder="全部" clearable>
            <el-option label="充值" value="recharge" />
            <el-option label="消费" value="consume" />
            <el-option label="退款" value="refund" />
            <el-option label="奖励" value="reward" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadTransactions">查询</el-button>
        </el-form-item>
      </el-form>

      <el-table v-loading="loading" :data="transactions" style="width: 100%">
        <el-table-column prop="id" label="交易ID" width="90" />
        <el-table-column label="交易类型" width="110">
          <template #default="{ row }">
            <el-tag :type="getTypeTagType(row.transaction_type)">
              {{ getTypeLabel(row.transaction_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="积分变化" width="120">
          <template #default="{ row }">
            <span :class="row.amount > 0 ? 'text-success' : 'text-danger'">
              {{ row.amount > 0 ? '+' : '' }}{{ row.amount }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="balance_after" label="余额" width="100" />
        <el-table-column prop="description" label="说明" min-width="220" />
        <el-table-column label="关联订单" width="150">
          <template #default="{ row }">
            <span v-if="row.order_id">{{ row.order_id }}</span>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column label="交易时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.size"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadTransactions"
          @current-change="loadTransactions"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Medal, Wallet } from '@element-plus/icons-vue'
import { getCreditBalance, getCreditTransactions, type CreditBalance } from '@/api/credit'

const router = useRouter()

interface Transaction {
  id: number
  transaction_type: string
  amount: number
  balance_after: number
  description: string
  order_id?: string
  created_at: string
}

const loading = ref(false)
const transactions = ref<Transaction[]>([])
const balance = ref<CreditBalance>({
  credits: 0,
  is_member: false,
  member_expired_at: null,
})

const filters = reactive({
  type: '',
})

const pagination = reactive({
  page: 1,
  size: 20,
  total: 0,
})

const getTypeLabel = (type: string) => {
  const labels: Record<string, string> = {
    recharge: '充值',
    consume: '消费',
    refund: '退款',
    reward: '奖励',
    expire: '过期',
  }
  return labels[type] || type
}

const getTypeTagType = (type: string) => {
  const types: Record<string, string> = {
    recharge: 'success',
    consume: 'warning',
    refund: 'info',
    reward: 'success',
    expire: 'danger',
  }
  return types[type] || ''
}

const formatDate = (date: string) => {
  return new Date(date).toLocaleString('zh-CN')
}

const loadBalance = async () => {
  try {
    const response = await getCreditBalance()
    balance.value = response.data
  } catch (error) {
    console.error('加载余额失败:', error)
  }
}

const loadTransactions = async () => {
  loading.value = true
  try {
    const params: any = {
      skip: (pagination.page - 1) * pagination.size,
      limit: pagination.size,
    }

    if (filters.type) {
      params.transaction_type = filters.type
    }

    const response: any = await getCreditTransactions(params)
    transactions.value = response.data.items
    pagination.total = response.data.total
  } catch (error: any) {
    ElMessage.error(error.response?.data?.message || '加载交易记录失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadBalance()
  loadTransactions()
})
</script>

<style scoped lang="scss">
.page-shell {
  display: flex;
  flex-direction: column;
  gap: 22px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-hero {
  position: relative;
  overflow: hidden;
  padding: 34px 30px;
  border-radius: 28px;
  background:
    radial-gradient(520px circle at 0% 0%, rgba(255, 255, 255, 0.18), transparent 55%),
    linear-gradient(135deg, #1d4ed8 0%, #0f6cde 44%, #38bdf8 100%);
  color: #fff;
  box-shadow: 0 24px 48px rgba(37, 99, 235, 0.22);

  &::after {
    content: '';
    position: absolute;
    inset: 16px;
    border-radius: 20px;
    border: 1px solid rgba(255, 255, 255, 0.2);
    pointer-events: none;
  }

  > div {
    position: relative;
    z-index: 1;
  }

  .eyebrow {
    margin-bottom: 10px;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    opacity: 0.8;
  }

  h1 {
    margin: 0 0 10px;
    font-size: 34px;
    font-weight: 700;
  }

  .description {
    max-width: 680px;
    margin: 0;
    font-size: 15px;
    line-height: 1.7;
    opacity: 0.92;
  }
}

.glass-card {
  border-radius: 24px;
  border: 1px solid rgba(37, 99, 235, 0.12);
  background: rgba(255, 255, 255, 0.82);
  box-shadow: 0 18px 36px rgba(15, 23, 42, 0.08);
  backdrop-filter: blur(14px);
}

.balance-info {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 20px;
  flex-wrap: wrap;
}

.balance-main {
  display: flex;
  gap: 28px;
  flex-wrap: wrap;
}

.balance-item {
  display: flex;
  flex-direction: column;
  gap: 8px;

  .label {
    color: #64748b;
    font-size: 14px;
  }

  .value {
    color: #0f172a;
    font-size: 20px;
    font-weight: 700;

    &.date {
      font-size: 15px;
    }
  }
}

.balance-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;

  span {
    color: #0f172a;
    font-size: 18px;
    font-weight: 700;
  }
}

.filter-form {
  margin-bottom: 18px;
  padding: 16px;
  border-radius: 18px;
  background: rgba(248, 250, 252, 0.9);
}

.text-success {
  color: #0f9f6e;
  font-weight: 700;
}

.text-danger {
  color: #ef4444;
  font-weight: 700;
}

.text-muted {
  color: #94a3b8;
}

.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

@media (max-width: 768px) {
  .page-hero {
    padding: 28px 22px;

    h1 {
      font-size: 28px;
    }
  }

  .balance-actions,
  .balance-main {
    width: 100%;
  }

  .pagination {
    justify-content: center;
    overflow-x: auto;
  }
}
</style>
