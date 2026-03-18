<template>
  <div class="credit-recharge page-shell">
    <section class="page-hero">
      <div>
        <p class="eyebrow">Credits</p>
        <h1>积分充值</h1>
        <p class="description">充值积分后即可继续调用创作能力，会员状态和充值记录会在这里统一管理。</p>
      </div>
    </section>

    <section class="overview-grid">
      <el-card class="balance-card glass-card">
        <div class="panel-head">
          <h3>当前账户</h3>
          <span>实时同步</span>
        </div>
        <div class="balance-info">
          <div class="balance-item main">
            <div class="label">当前积分</div>
            <div class="value">{{ balance.credits }}</div>
          </div>
          <div class="balance-item">
            <div class="label">会员状态</div>
            <div class="value">
              <el-tag v-if="balance.is_member" type="success">会员</el-tag>
              <el-tag v-else type="info">普通用户</el-tag>
            </div>
          </div>
          <div v-if="balance.is_member && balance.member_expired_at" class="balance-item">
            <div class="label">到期时间</div>
            <div class="value date">{{ formatDate(balance.member_expired_at) }}</div>
          </div>
        </div>
      </el-card>

      <el-card class="price-card glass-card">
        <template #header>
          <div class="card-header">
            <span>选择套餐</span>
            <span class="tip">1 元 = 100 积分</span>
          </div>
        </template>
        <div class="price-list">
          <div
            v-for="price in prices"
            :key="price.id"
            class="price-item"
            :class="{ active: selectedPrice?.id === price.id, hot: price.bonus_credits > 0 }"
            @click="selectPrice(price)"
          >
            <div v-if="price.bonus_credits > 0" class="badge">赠送</div>
            <div class="amount">{{ price.credits }}<span class="unit">积分</span></div>
            <div v-if="price.bonus_credits > 0" class="bonus">+{{ price.bonus_credits }} 积分</div>
            <div class="price">￥{{ price.amount }}</div>
            <div v-if="price.bonus_credits > 0" class="total">实得 {{ price.credits + price.bonus_credits }} 积分</div>
          </div>
        </div>
      </el-card>
    </section>

    <el-card v-if="selectedPrice" class="payment-card glass-card">
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
          <span>充值积分</span>
          <span>{{ selectedPrice.credits }} 积分</span>
        </div>
        <div v-if="selectedPrice.bonus_credits > 0" class="summary-item">
          <span>赠送积分</span>
          <span class="bonus-text">+{{ selectedPrice.bonus_credits }} 积分</span>
        </div>
        <div class="summary-item total">
          <span>实付金额</span>
          <span class="price-text">￥{{ selectedPrice.amount }}</span>
        </div>
      </div>

      <el-button type="primary" size="large" :loading="loading" @click="handleRecharge" class="pay-button">
        立即支付
      </el-button>
    </el-card>

    <el-card class="history-card glass-card">
      <template #header>
        <div class="card-header">
          <span>充值记录</span>
          <el-button text type="primary" @click="loadOrders">刷新</el-button>
        </div>
      </template>

      <div class="table-view">
        <el-table :data="orders" style="width: 100%">
          <el-table-column prop="order_no" label="订单号" width="200" />
          <el-table-column label="充值积分" width="130">
            <template #default="{ row }">
              {{ row.credits }}
              <span v-if="row.bonus_credits > 0" class="bonus-text">+{{ row.bonus_credits }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="amount" label="支付金额" width="110">
            <template #default="{ row }">￥{{ row.amount }}</template>
          </el-table-column>
          <el-table-column prop="payment_method" label="支付方式" width="110">
            <template #default="{ row }">
              {{ row.payment_method === 'alipay' ? '支付宝' : '微信支付' }}
            </template>
          </el-table-column>
          <el-table-column prop="payment_status" label="状态" width="110">
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
              <el-button v-if="row.payment_status === 'pending'" text type="primary" @click="handleSimulatePayment(row)">
                模拟支付
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

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
              <span>充值积分</span>
              <span>{{ order.credits }}<span v-if="order.bonus_credits > 0" class="bonus-text">+{{ order.bonus_credits }}</span></span>
            </div>
            <div class="info-row">
              <span>支付金额</span>
              <span>￥{{ order.amount }}</span>
            </div>
            <div class="info-row">
              <span>创建时间</span>
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
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { CreditCard, Wallet } from '@element-plus/icons-vue'
import {
  createRechargeOrder,
  getCreditBalance,
  getCreditPrices,
  getRechargeOrders,
  simulatePayment,
  type CreditBalance,
  type CreditPrice,
  type RechargeOrder,
} from '@/api/credit'

const balance = ref<CreditBalance>({
  credits: 0,
  is_member: false,
  member_expired_at: null,
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
    prices.value = Array.isArray(res.data) ? res.data : (res.data?.items || [])
    if (!selectedPrice.value && prices.value.length > 0) {
      selectedPrice.value = prices.value[0]
    }
  } catch (error) {
    console.error('加载价格失败:', error)
  }
}

const loadOrders = async () => {
  try {
    const res = await getRechargeOrders({ limit: 10 })
    orders.value = (res.data as any)?.items || res.data || []
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
    await createRechargeOrder({
      price_id: selectedPrice.value.id,
      payment_method: paymentMethod.value,
    })
    ElMessage.success('订单创建成功，请完成支付')
    await loadOrders()
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
      order_no: order.order_no,
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

.overview-grid {
  display: grid;
  grid-template-columns: 0.95fr 1.05fr;
  gap: 20px;
}

.glass-card {
  border-radius: 24px;
  border: 1px solid rgba(37, 99, 235, 0.12);
  background: rgba(255, 255, 255, 0.82);
  box-shadow: 0 18px 36px rgba(15, 23, 42, 0.08);
  backdrop-filter: blur(14px);
}

.panel-head,
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;

  h3,
  span:first-child {
    color: #0f172a;
    font-size: 18px;
    font-weight: 700;
  }

  span:last-child,
  .tip {
    color: #64748b;
    font-size: 13px;
    font-weight: 600;
  }
}

.balance-info {
  display: flex;
  flex-wrap: wrap;
  gap: 28px;
  margin-top: 18px;
}

.balance-item {
  .label {
    margin-bottom: 8px;
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

  &.main .value {
    font-size: 36px;
    color: #2563eb;
  }
}

.price-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 16px;
}

.price-item {
  position: relative;
  padding: 20px 16px;
  border-radius: 20px;
  border: 1px solid rgba(37, 99, 235, 0.1);
  background: rgba(255, 255, 255, 0.74);
  text-align: center;
  cursor: pointer;
  transition: all 0.25s ease;

  &:hover {
    transform: translateY(-4px);
    border-color: rgba(37, 99, 235, 0.22);
    box-shadow: 0 18px 28px rgba(37, 99, 235, 0.12);
  }

  &.active {
    border-color: rgba(37, 99, 235, 0.24);
    background: linear-gradient(180deg, rgba(239, 246, 255, 0.92), rgba(255, 255, 255, 0.84));
  }

  &.hot {
    border-color: rgba(239, 68, 68, 0.22);
  }

  .badge {
    position: absolute;
    top: 12px;
    right: 12px;
    padding: 5px 10px;
    border-radius: 999px;
    background: linear-gradient(135deg, #ef4444, #f97316);
    color: #fff;
    font-size: 12px;
    font-weight: 700;
    box-shadow: 0 10px 18px rgba(239, 68, 68, 0.16);
  }

  .amount {
    margin-bottom: 6px;
    color: #0f172a;
    font-size: 24px;
    font-weight: 700;

    .unit {
      margin-left: 4px;
      color: #64748b;
      font-size: 13px;
      font-weight: 500;
    }
  }

  .bonus {
    margin-bottom: 8px;
    color: #ef4444;
    font-size: 14px;
    font-weight: 700;
  }

  .price {
    margin-bottom: 6px;
    color: #2563eb;
    font-size: 22px;
    font-weight: 700;
  }

  .total {
    color: #64748b;
    font-size: 12px;
  }
}

.payment-methods {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
  margin-bottom: 20px;
}

.payment-label {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.payment-summary {
  margin-bottom: 20px;
  padding: 20px;
  border-radius: 18px;
  background: rgba(248, 250, 252, 0.9);
}

.summary-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
  color: #475569;
  font-size: 14px;

  &:last-child {
    margin-bottom: 0;
  }

  &.total {
    padding-top: 12px;
    border-top: 1px solid rgba(37, 99, 235, 0.08);
    font-size: 16px;
    font-weight: 700;
  }
}

.bonus-text {
  color: #ef4444;
  font-weight: 700;
}

.price-text {
  color: #2563eb;
  font-size: 24px;
}

.pay-button {
  width: 100%;
  height: 46px;
  border-radius: 12px;
  font-weight: 700;
}

.history-card {
  .bonus-text {
    margin-left: 4px;
  }
}

.table-view {
  display: block;
}

.card-view {
  display: none;
}

.order-card {
  padding: 16px;
  border-radius: 18px;
  border: 1px solid rgba(37, 99, 235, 0.1);
  background: rgba(255, 255, 255, 0.72);
  margin-bottom: 12px;

  .order-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 12px;
  }

  .order-no {
    color: #64748b;
    font-size: 12px;
  }

  .info-row {
    display: flex;
    justify-content: space-between;
    margin-bottom: 8px;
    color: #475569;
    font-size: 14px;
  }

  .order-footer {
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px solid rgba(37, 99, 235, 0.08);
    text-align: right;
  }
}

@media (max-width: 900px) {
  .overview-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .page-hero {
    padding: 28px 22px;

    h1 {
      font-size: 28px;
    }
  }

  .price-list {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }

  .price-item {
    padding: 16px 12px;

    .amount {
      font-size: 20px;
    }

    .price {
      font-size: 18px;
    }
  }

  .table-view {
    display: none;
  }

  .card-view {
    display: block;
  }
}
</style>
