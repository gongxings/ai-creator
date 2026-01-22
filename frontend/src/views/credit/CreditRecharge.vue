<template>
  <div class="credit-recharge">
    <el-card class="balance-card">
      <template #header>
        <div class="card-header">
          <span>我的账户</span>
        </div>
      </template>
      <div class="balance-info">
        <div class="balance-item">
          <div class="label">当前积分</div>
          <div class="value">{{ balance.credits }}</div>
        </div>
        <div class="balance-item">
          <div class="label">会员状态</div>
          <div class="value">
            <el-tag v-if="balance.is_member" type="success">会员</el-tag>
            <el-tag v-else type="info">非会员</el-tag>
          </div>
        </div>
        <div v-if="balance.is_member && balance.member_expired_at" class="balance-item">
          <div class="label">到期时间</div>
          <div class="value">{{ formatDate(balance.member_expired_at) }}</div>
        </div>
      </div>
    </el-card>

    <el-card class="price-card">
      <template #header>
        <div class="card-header">
          <span>积分充值</span>
          <span class="tip">1元 = 10积分，每次生成消耗10积分</span>
        </div>
      </template>
      <div class="price-list">
        <div
          v-for="price in prices"
          :key="price.id"
          class="price-item"
          :class="{ active: selectedPrice?.id === price.id }"
          @click="selectPrice(price)"
        >
          <div class="amount">{{ price.amount }}积分</div>
          <div v-if="price.bonus > 0" class="bonus">送{{ price.bonus }}积分</div>
          <div class="price">¥{{ price.price }}</div>
          <div v-if="price.bonus > 0" class="total">
            实得{{ price.amount + price.bonus }}积分
          </div>
        </div>
      </div>
    </el-card>

    <el-card v-if="selectedPrice" class="payment-card">
      <template #header>
        <div class="card-header">
          <span>支付方式</span>
        </div>
      </template>
      <el-radio-group v-model="paymentMethod" class="payment-methods">
        <el-radio label="alipay">
          <span class="payment-label">
            <el-icon><CreditCard /></el-icon>
            支付宝
          </span>
        </el-radio>
        <el-radio label="wechat">
          <span class="payment-label">
            <el-icon><Wallet /></el-icon>
            微信支付
          </span>
        </el-radio>
      </el-radio-group>

      <div class="payment-summary">
        <div class="summary-item">
          <span>充值积分：</span>
          <span>{{ selectedPrice.amount }}积分</span>
        </div>
        <div v-if="selectedPrice.bonus > 0" class="summary-item">
          <span>赠送积分：</span>
          <span class="bonus-text">{{ selectedPrice.bonus }}积分</span>
        </div>
        <div class="summary-item total">
          <span>实付金额：</span>
          <span class="price-text">¥{{ selectedPrice.price }}</span>
        </div>
      </div>

      <el-button
        type="primary"
        size="large"
        :loading="loading"
        @click="handleRecharge"
        class="pay-button"
      >
        立即支付
      </el-button>
    </el-card>

    <el-card class="history-card">
      <template #header>
        <div class="card-header">
          <span>充值记录</span>
          <el-button text @click="loadOrders">刷新</el-button>
        </div>
      </template>
      <el-table :data="orders" style="width: 100%">
        <el-table-column prop="order_no" label="订单号" width="200" />
        <el-table-column label="充值积分" width="120">
          <template #default="{ row }">
            {{ row.amount }}
            <span v-if="row.bonus > 0" class="bonus-text">+{{ row.bonus }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="price" label="支付金额" width="100">
          <template #default="{ row }">¥{{ row.price }}</template>
        </el-table-column>
        <el-table-column prop="payment_method" label="支付方式" width="100">
          <template #default="{ row }">
            {{ row.payment_method === 'alipay' ? '支付宝' : '微信支付' }}
          </template>
        </el-table-column>
        <el-table-column prop="payment_status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.payment_status === 'paid'" type="success">已支付</el-tag>
            <el-tag v-else-if="row.payment_status === 'pending'" type="warning">待支付</el-tag>
            <el-tag v-else-if="row.payment_status === 'failed'" type="danger">失败</el-tag>
            <el-tag v-else type="info">{{ row.payment_status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button
              v-if="row.payment_status === 'pending'"
              text
              type="primary"
              @click="handleSimulatePayment(row)"
            >
              模拟支付
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { CreditCard, Wallet } from '@element-plus/icons-vue'
import {
  getCreditBalance,
  getCreditPrices,
  createRechargeOrder,
  getRechargeOrders,
  simulatePayment,
  type CreditBalance,
  type CreditPrice,
  type RechargeOrder
} from '@/api/credit'

const balance = ref<CreditBalance>({
  credits: 0,
  is_member: false,
  member_expired_at: null
})

const prices = ref<CreditPrice[]>([])
const selectedPrice = ref<CreditPrice | null>(null)
const paymentMethod = ref('alipay')
const loading = ref(false)
const orders = ref<RechargeOrder[]>([])

const loadBalance = async () => {
  try {
    const res = await getCreditBalance()
    balance.value = res.data
  } catch (error) {
    console.error('加载余额失败:', error)
  }
}

const loadPrices = async () => {
  try {
    const res = await getCreditPrices()
    prices.value = res.data
  } catch (error) {
    console.error('加载价格失败:', error)
  }
}

const loadOrders = async () => {
  try {
    const res = await getRechargeOrders({ limit: 10 })
    orders.value = res.data
  } catch (error) {
    console.error('加载订单失败:', error)
  }
}

const selectPrice = (price: CreditPrice) => {
  selectedPrice.value = price
}

const handleRecharge = async () => {
  if (!selectedPrice.value) {
    ElMessage.warning('请选择充值套餐')
    return
  }

  loading.value = true
  try {
    const res = await createRechargeOrder({
      price_id: selectedPrice.value.id,
      payment_method: paymentMethod.value
    })
    
    ElMessage.success('订单创建成功，请完成支付')
    await loadOrders()
    
    // 在实际应用中，这里应该跳转到支付页面
    // 这里我们提供一个模拟支付的按钮
  } catch (error: any) {
    ElMessage.error(error.response?.data?.message || '创建订单失败')
  } finally {
    loading.value = false
  }
}

const handleSimulatePayment = async (order: RechargeOrder) => {
  try {
    await simulatePayment({
      order_type: 'recharge',
      order_no: order.order_no
    })
    
    ElMessage.success('支付成功')
    await loadBalance()
    await loadOrders()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.message || '支付失败')
  }
}

const formatDate = (date: string) => {
  return new Date(date).toLocaleString('zh-CN')
}

onMounted(() => {
  loadBalance()
  loadPrices()
  loadOrders()
})
</script>

<style scoped lang="scss">
.credit-recharge {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .tip {
      font-size: 14px;
      color: #909399;
      font-weight: normal;
    }
  }

  .balance-card {
    margin-bottom: 20px;

    .balance-info {
      display: flex;
      gap: 40px;

      .balance-item {
        .label {
          font-size: 14px;
          color: #909399;
          margin-bottom: 8px;
        }

        .value {
          font-size: 24px;
          font-weight: bold;
          color: #303133;
        }
      }
    }
  }

  .price-card {
    margin-bottom: 20px;

    .price-list {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
      gap: 16px;

      .price-item {
        border: 2px solid #dcdfe6;
        border-radius: 8px;
        padding: 20px;
        cursor: pointer;
        transition: all 0.3s;
        text-align: center;

        &:hover {
          border-color: #409eff;
          box-shadow: 0 2px 12px rgba(64, 158, 255, 0.2);
        }

        &.active {
          border-color: #409eff;
          background-color: #ecf5ff;
        }

        .amount {
          font-size: 20px;
          font-weight: bold;
          color: #303133;
          margin-bottom: 8px;
        }

        .bonus {
          font-size: 14px;
          color: #f56c6c;
          margin-bottom: 8px;
        }

        .price {
          font-size: 24px;
          font-weight: bold;
          color: #409eff;
          margin-bottom: 8px;
        }

        .total {
          font-size: 12px;
          color: #909399;
        }
      }
    }
  }

  .payment-card {
    margin-bottom: 20px;

    .payment-methods {
      display: flex;
      gap: 20px;
      margin-bottom: 20px;

      .payment-label {
        display: flex;
        align-items: center;
        gap: 8px;
      }
    }

    .payment-summary {
      background-color: #f5f7fa;
      border-radius: 8px;
      padding: 20px;
      margin-bottom: 20px;

      .summary-item {
        display: flex;
        justify-content: space-between;
        margin-bottom: 12px;
        font-size: 14px;

        &:last-child {
          margin-bottom: 0;
        }

        &.total {
          font-size: 16px;
          font-weight: bold;
          padding-top: 12px;
          border-top: 1px solid #dcdfe6;
        }

        .bonus-text {
          color: #f56c6c;
        }

        .price-text {
          color: #409eff;
          font-size: 20px;
        }
      }
    }

    .pay-button {
      width: 100%;
    }
  }

  .history-card {
    .bonus-text {
      color: #f56c6c;
      margin-left: 4px;
    }
  }
}
</style>
