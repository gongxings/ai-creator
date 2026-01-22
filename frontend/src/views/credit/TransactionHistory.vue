<template>
  <div class="transaction-history">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>交易记录</span>
          <el-button type="primary" @click="loadTransactions">刷新</el-button>
        </div>
      </template>

      <!-- 筛选条件 -->
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

      <!-- 交易列表 -->
      <el-table
        v-loading="loading"
        :data="transactions"
        style="width: 100%"
      >
        <el-table-column prop="id" label="交易ID" width="80" />
        <el-table-column label="交易类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getTypeTagType(row.transaction_type)">
              {{ getTypeLabel(row.transaction_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="积分变动" width="120">
          <template #default="{ row }">
            <span :class="row.amount > 0 ? 'text-success' : 'text-danger'">
              {{ row.amount > 0 ? '+' : '' }}{{ row.amount }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="balance_after" label="余额" width="100" />
        <el-table-column prop="description" label="说明" min-width="200" />
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

      <!-- 分页 -->
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
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getTransactions } from '@/api/credit'

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
  const types: Record<string, any> = {
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

    const response = await getTransactions(params)
    transactions.value = response.data.items
    pagination.total = response.data.total
  } catch (error: any) {
    ElMessage.error(error.response?.data?.message || '加载交易记录失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadTransactions()
})
</script>

<style scoped>
.transaction-history {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-form {
  margin-bottom: 20px;
}

.text-success {
  color: #67c23a;
  font-weight: bold;
}

.text-danger {
  color: #f56c6c;
  font-weight: bold;
}

.text-muted {
  color: #909399;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
