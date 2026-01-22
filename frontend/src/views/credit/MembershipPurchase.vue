<template>
  <div class="membership-purchase">
    <el-card class="status-card">
      <template #header>
        <div class="card-header">
          <span>会员状态</span>
        </div>
      </template>
      <div class="status-info">
        <div class="status-item">
          <div class="label">当前状态</div>
          <div class="value">
            <el-tag v-if="balance.is_member" type="success" size="large">
              会员用户
            </el-tag>
            <el-tag v-else type="info" size="large">
              普通用户
            </el-tag>
          </div>
        </div>
        <div v-if="balance.is_member && balance.member_expired_at" class="status-item">
          <div class="label">到期时间</div>
          <div class="value">{{ formatDate(balance.member_expired_at) }}</div>
        </div>
        <div class="status-item">
          <div class="label">当前积分</div>
          <div class="value">{{ balance.credits }}</div>
        </div>
      </div>
    </el-card>

    <el-card class="benefits-card">
      <template #header>
        <div class="card-header">
          <span>会员权益</span>
        </div>
      </template>
      <div class="benefits-list">
        <div class="benefit-item">
          <el-icon class="icon" color="#67c23a"><Check /></el-icon>
          <div class="content">
            <div class="title">无限制使用</div>
            <div class="desc">所有AI创作工具不限次数使用</div>
          </div>
        </div>
        <div class="benefit-item">
          <el-icon class="icon" color="#67c23a"><Check /></el-icon>
          <div class="content">
            <div class="title">不扣积分</div>
            <div class="desc">会员期间生成内容不消耗积分</div>
          </div>
        </div>
        <div class="benefit-item">
          <el-icon class="icon" color="#67c23a"><Check /></el-icon>
          <div class="content">
            <div class="title">优先支持</div>
            <div class="desc">享受优先客服支持和问题处理</div>
          </div>
        </div>
        <div class="benefit-item">
          <el-icon class="icon" color="#67c23a"><Check /></el-icon>
          <div class="content">
            <div class="title">新功能优先体验</div>
            <div class="desc">第一时间体验平台新功能</div>
          </div>
        </div>
      </div>
    </el-card>

    <el-card class="price-card">
      <template #header>
        <div class="card-header">
          <span>选择套餐</span>
        </div>
      </template>
      <div class="price-list">
        <div
          v-for="price in prices"
          :key="price.id"
          class="price-item"
          :class="{ 
            active: selectedPrice?.id === price.id,
            recommended: price.membership_type === 'yearly'
          }"
          @click="selectPrice(price)"
        >
          <div v-if="price.membership_type === 'yearly'" class="badge">推荐</div>
          <div class="type">{{ getMembershipTypeName(price.membership_type) }}</div>
          <div class="duration">{{ price.duration_days }}天</div>
          <div class="price">
            <span class="current">¥{{ price.price }}</span>
            <span class="original">¥{{ price.original_price }}</span>
          </div>
          <div class="discount">
            省¥{{ (price.original_price - price.price).toFixed(2) }}
          </div>
          <div class="daily">
            每天仅需¥{{ (price.price / price.duration_days).toFixed(2) }}
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
          <span>套餐类型：</span>
          <span>{{ getMembershipTypeName(selectedPrice.membership_type) }}</span>
        </div>
        <div class="summary-item">
          <span>有效期：</span>
          <span>{{ selectedPrice.duration_days }}天</span>
        </div>
        <div class="summary-item">
          <span>原价：</span>
          <span class="original-price">¥{{ selectedPrice.original_price }}</span>
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
        @click="handlePurchase"
        class="pay-button"
      >
        立即开通
      </el-button>
    </el-card>

    <el-card class="history-card">
      <template #header>
        <div class="card-header">
          <span>购买记录</span>
          <el-button text @click="loadOrders">刷新</el-button>
        </div>
      </template>
      <el-table :data="orders" style="width: 100%">
        <el-table-column prop="order_no" label="订单号" width="200" />
        <el-table-column prop="membership_type" label="套餐类型" width="120">
          <template #default="{ row }">
            {{ getMembershipTypeName(row.membership_type) }}
          </template>
        </el-table-column>
        <el-table-column prop="duration_days" label="有效期" width="100">
          <template #default="{ row }">{{ row.duration_days }}天</template>
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
        <el-table-column label="有效期" width="200">
          <template #default="{ row }">
            <span v-if="row.start_date && row.end_date">
              {{ formatDate(row.start_date) }} 至 {{ formatDate(row.end_date) }}
            </span>
            <span v-else>-</span>
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
import { CreditCard, Wallet, Check } from '@element-plus/icons-vue'
import {
  getCreditBalance,
  getMembershipPrices,
  createMembershipOrder,
  getMembershipOrders,
  simulatePayment,
  type CreditBalance,
  type MembershipPrice,
  type MembershipOrder
} from '@/api/credit'

const balance = ref<CreditBalance>({
  credits: 0,
  is_member: false,
  member_expired_at: null
})

const prices = ref<MembershipPrice[]>([])
const selectedPrice = ref<MembershipPrice | null>(null)
const paymentMethod = ref('alipay')
const loading = ref(false)
const orders = ref<MembershipOrder[]>([])

const membershipTypeMap: Record<string, string> = {
  monthly: '月度会员',
  quarterly: '季度会员',
  yearly: '年度会员'
}

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
    const res = await getMembershipPrices()
    prices.value = res.data
  } catch (error) {
    console.error('加载价格失败:', error)
  }
}

const loadOrders = async () => {
  try {
    const res = await getMembershipOrders({ limit: 10 })
    orders.value = res.data
  } catch (error) {
    console.error('加载订单失败:', error)
  }
}

const selectPrice = (price: MembershipPrice) => {
  selectedPrice.value = price
}

const getMembershipTypeName = (type: string) => {
  return membershipTypeMap[type] || type
}

const handlePurchase = async () => {
  if (!selectedPrice.value) {
    ElMessage.warning('请选择会员套餐')
    return
  }

  loading.value = true
  try {
    const res = await createMembershipOrder({
      price_id: selectedPrice.value.id,
      payment_method: paymentMethod.value
    })
    
    ElMessage.success('订单创建成功，请完成支付')
    await loadOrders()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.message || '创建订单失败')
  } finally {
    loading.value = false
  }
}

const handleSimulatePayment = async (order: MembershipOrder) => {
  try {
    await simulatePayment({
      order_type: 'membership',
      order_no: order.order_no
    })
    
    ElMessage.success('支付成功，会员已开通')
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
.membership-purchase {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .status-card {
    margin-bottom: 20px;

    .status-info {
      display: flex;
      gap: 40px;

      .status-item {
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

  .benefits-card {
    margin-bottom: 20px;

    .benefits-list {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 20px;

      .benefit-item {
        display: flex;
        gap: 12px;
        align-items: flex-start;

        .icon {
          font-size: 24px;
          flex-shrink: 0;
        }

        .content {
          .title {
            font-size: 16px;
            font-weight: bold;
            color: #303133;
            margin-bottom: 4px;
          }

          .desc {
            font-size: 14px;
            color: #909399;
          }
        }
      }
    }
  }

  .price-card {
    margin-bottom: 20px;

    .price-list {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 20px;

      .price-item {
        position: relative;
        border: 2px solid #dcdfe6;
        border-radius: 8px;
        padding: 24px;
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

        &.recommended {
          border-color: #67c23a;

          .badge {
            position: absolute;
            top: -10px;
            right: 20px;
            background: linear-gradient(135deg, #67c23a, #85ce61);
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
          }
        }

        .type {
          font-size: 20px;
          font-weight: bold;
          color: #303133;
          margin-bottom: 8px;
        }

        .duration {
          font-size: 14px;
          color: #909399;
          margin-bottom: 12px;
        }

        .price {
          margin-bottom: 8px;

          .current {
            font-size: 32px;
            font-weight: bold;
            color: #409eff;
            margin-right: 8px;
          }

          .original {
            font-size: 16px;
            color: #909399;
            text-decoration: line-through;
          }
        }

        .discount {
          font-size: 14px;
          color: #f56c6c;
          margin-bottom: 8px;
        }

        .daily {
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

        .original-price {
          color: #909399;
          text-decoration: line-through;
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
}
</style>
