<template>
  <div class="credit-recharge">
    <el-card class="header-card">
      <div class="header-content">
        <div class="header-left">
          <h2>积分充值</h2>
          <p class="subtitle">充值积分，畅享AI创作</p>
        </div>
      </div>
    </el-card>

    <el-card class="balance-card">
      <div class="balance-info">
        <div class="balance-item main">
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
          <div class="value date">{{ formatDate(balance.member_expired_at) }}</div>
        </div>
      </div>
    </el-card>

    <el-card class="price-card">
      <template #header>
        <div class="card-header">
          <span>选择套餐</span>
          <span class="tip">1元 = 10积分</span>
        </div>
      </template>
      <div class="price-list">
        <div
          v-for="price in prices"
          :key="price.id"
          class="price-item"
          :class="{ active: selectedPrice?.id === price.id, hot: price.bonus > 0 }"
          @click="selectPrice(price)"
        >
          <div v-if="price.bonus > 0" class="badge">赠送</div>
          <div class="amount">{{ price.amount }}<span class="unit">积分</span></div>
          <div v-if="price.bonus > 0" class="bonus">+{{ price.bonus }}积分</div>
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
          <span class="bonus-text">+{{ selectedPrice.bonus }}积分</span>
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
          <el-button text type="primary" @click="loadOrders">刷新</el-button>
        </div>
      </template>

      <!-- 桌面版表格 -->
      <div class="table-view">
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
      </div>

      <!-- 手机版卡片 -->
      <div v-if="orders.length > 0" class="card-view">
        <div v-for="order in orders" :key="order.order_no" class="order-card">
          <div class="order-header">
            <span class="order-no">{{ order.order_no }}</span>
            <el-tag v-if="order.payment_status === 'paid'" type="success" size="small">已支付</el-tag>
            <el-tag v-else-if="order.payment_status === 'pending'" type="warning" size="small">待支付</el-tag>
            <el-tag v-else type="danger" size="small">{{ order.payment_status }}</el-tag>
          </div>
          <div class="order-body">
            <div class="info-row">
              <span>充值积分：</span>
              <span>{{ order.amount }}<span v-if="order.bonus > 0" class="bonus-text">+{{ order.bonus }}</span></span>
            </div>
            <div class="info-row">
              <span>支付金额：</span>
              <span>¥{{ order.price }}</span>
            </div>
            <div class="info-row">
              <span>创建时间：</span>
              <span>{{ formatDate(order.created_at) }}</span>
            </div>
          </div>
          <div v-if="order.payment_status === 'pending'" class="order-footer">
            <el-button type="primary" size="small" @click="handleSimulatePayment(order)">模拟支付</el-button>
          </div>
        </div>
      </div>

      <el-empty v-else description="暂无充值记录" />
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
      flex-wrap: wrap;

      .balance-item {
        .label {
          font-size: 14px;
          color: #909399;
          margin-bottom: 8px;
        }

        .value {
          font-size: 20px;
          font-weight: bold;
          color: #303133;

          &.date {
            font-size: 16px;
          }
        }

        &.main .value {
          font-size: 32px;
          color: #409eff;
        }
      }
    }
  }

  .price-card {
    margin-bottom: 20px;

    .price-list {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
      gap: 16px;

      .price-item {
        position: relative;
        border: 2px solid #edf2f7;
        border-radius: 12px;
        padding: 20px 16px;
        cursor: pointer;
        transition: all 0.3s;
        text-align: center;
        background: #fff;

        &:hover {
          border-color: #409eff;
          box-shadow: 0 4px 16px rgba(64, 158, 255, 0.15);
          transform: translateY(-2px);
        }

        &.active {
          border-color: #409eff;
          background: linear-gradient(135deg, #ecf5ff 0%, #f0f9ff 100%);
        }

        &.hot {
          border-color: #f56c6c;

          .badge {
            position: absolute;
            top: -10px;
            right: 10px;
            background: linear-gradient(135deg, #f56c6c, #ff7875);
            color: white;
            padding: 4px 10px;
            border-radius: 10px;
            font-size: 12px;
            font-weight: bold;
          }
        }

        .amount {
          font-size: 24px;
          font-weight: bold;
          color: #1f2937;
          margin-bottom: 6px;

          .unit {
            font-size: 14px;
            font-weight: normal;
            color: #64748b;
          }
        }

        .bonus {
          font-size: 14px;
          color: #f56c6c;
          margin-bottom: 8px;
          font-weight: 600;
        }

        .price {
          font-size: 20px;
          font-weight: bold;
          color: #409eff;
          margin-bottom: 6px;
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
      flex-wrap: wrap;

      .payment-label {
        display: flex;
        align-items: center;
        gap: 8px;
      }
    }

    .payment-summary {
      background-color: #f8fafc;
      border-radius: 12px;
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
          border-top: 1px solid #e5e7eb;
        }

        .bonus-text {
          color: #f56c6c;
          font-weight: 600;
        }

        .price-text {
          color: #409eff;
          font-size: 24px;
        }
      }
    }

    .pay-button {
      width: 100%;
    }
  }

  .history-card {
    .table-view {
      display: block;
    }

    .card-view {
      display: none;
    }

    .bonus-text {
      color: #f56c6c;
      margin-left: 4px;
    }

    .order-card {
      background: #fff;
      border: 1px solid #edf2f7;
      border-radius: 12px;
      padding: 16px;
      margin-bottom: 12px;

      .order-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;

        .order-no {
          font-size: 12px;
          color: #64748b;
        }
      }

      .order-body {
        .info-row {
          display: flex;
          justify-content: space-between;
          font-size: 14px;
          margin-bottom: 8px;
          color: #64748b;
        }
      }

      .order-footer {
        padding-top: 12px;
        border-top: 1px solid #f1f5f9;
        margin-top: 12px;
        text-align: right;
      }
    }
  }
}

@media (max-width: 768px) {
  .credit-recharge {
    padding: 12px;

    .balance-card {
      .balance-info {
        gap: 24px;

        .balance-item.main .value {
          font-size: 28px;
        }
      }
    }

    .price-card {
      .price-list {
        grid-template-columns: repeat(2, 1fr);
        gap: 12px;

        .price-item {
          padding: 16px 12px;

          .amount {
            font-size: 20px;
          }

          .price {
            font-size: 18px;
          }
        }
      }
    }

    .history-card {
      .table-view {
        display: none;
      }

      .card-view {
        display: block;
      }
    }
  }
}
</style>
