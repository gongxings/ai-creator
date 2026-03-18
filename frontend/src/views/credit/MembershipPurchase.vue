<template>
  <div class="membership-purchase page-shell">
    <section class="page-hero">
      <div>
        <p class="eyebrow">Membership</p>
        <h1>会员购买</h1>
        <p class="description">开通会员后可持续使用创作能力，减少积分消耗并获得更稳定的服务支持。</p>
      </div>
    </section>

    <section class="overview-grid">
      <el-card class="status-card glass-card">
        <div class="panel-head">
          <h3>当前状态</h3>
          <span>账户概览</span>
        </div>
        <div class="status-info">
          <div class="status-item main">
            <div class="label">会员身份</div>
            <div class="value">
              <el-tag v-if="balance.is_member" type="success" size="large">会员用户</el-tag>
              <el-tag v-else type="info" size="large">普通用户</el-tag>
            </div>
          </div>
          <div v-if="balance.is_member && balance.member_expired_at" class="status-item">
            <div class="label">到期时间</div>
            <div class="value date">{{ formatDate(balance.member_expired_at) }}</div>
          </div>
          <div class="status-item">
            <div class="label">当前积分</div>
            <div class="value">{{ balance.credits }}</div>
          </div>
        </div>
      </el-card>

      <el-card class="benefits-card glass-card">
        <template #header>
          <div class="card-header">
            <span>会员专属权益</span>
          </div>
        </template>
        <div class="benefits-list">
          <div class="benefit-item">
            <el-icon class="icon" color="#0f9f6e"><Check /></el-icon>
            <div class="content">
              <div class="title">不限次数使用</div>
              <div class="desc">会员期内可持续调用主要创作工具。</div>
            </div>
          </div>
          <div class="benefit-item">
            <el-icon class="icon" color="#0f9f6e"><Check /></el-icon>
            <div class="content">
              <div class="title">减少积分消耗</div>
              <div class="desc">高频创作场景下更适合长期使用。</div>
            </div>
          </div>
          <div class="benefit-item">
            <el-icon class="icon" color="#0f9f6e"><Check /></el-icon>
            <div class="content">
              <div class="title">优先服务支持</div>
              <div class="desc">享受更快的响应和问题处理效率。</div>
            </div>
          </div>
          <div class="benefit-item">
            <el-icon class="icon" color="#0f9f6e"><Check /></el-icon>
            <div class="content">
              <div class="title">新功能优先体验</div>
              <div class="desc">更早使用新的创作能力与工具模块。</div>
            </div>
          </div>
        </div>
      </el-card>
    </section>

    <el-card class="price-card glass-card">
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
          :class="{ active: selectedPrice?.id === price.id, recommended: price.membership_type === 'yearly' }"
          @click="selectPrice(price)"
        >
          <div v-if="price.membership_type === 'yearly'" class="badge">推荐</div>
          <div class="type">{{ getMembershipTypeName(price.membership_type) }}</div>
          <div class="duration">{{ price.duration_days }} 天</div>
          <div class="price">
            <span class="current">￥{{ price.amount }}</span>
            <span v-if="price.original_amount" class="original">￥{{ price.original_amount }}</span>
          </div>
          <div v-if="price.original_amount" class="discount">立省 ￥{{ (price.original_amount - price.amount).toFixed(0) }}</div>
          <div class="daily">折合每天 ￥{{ (price.amount / price.duration_days).toFixed(2) }}</div>
        </div>
      </div>
    </el-card>

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
          <span>套餐类型</span>
          <span>{{ getMembershipTypeName(selectedPrice.membership_type) }}</span>
        </div>
        <div class="summary-item">
          <span>有效期</span>
          <span>{{ selectedPrice.duration_days }} 天</span>
        </div>
        <div v-if="selectedPrice.original_amount" class="summary-item">
          <span>原价</span>
          <span class="original-price">￥{{ selectedPrice.original_amount }}</span>
        </div>
        <div class="summary-item total">
          <span>实付金额</span>
          <span class="price-text">￥{{ selectedPrice.amount }}</span>
        </div>
      </div>

      <el-button type="primary" size="large" :loading="loading" @click="handlePurchase" class="pay-button">
        立即开通
      </el-button>
    </el-card>

    <el-card class="history-card glass-card">
      <template #header>
        <div class="card-header">
          <span>购买记录</span>
          <el-button text type="primary" @click="loadOrders">刷新</el-button>
        </div>
      </template>

      <div class="table-view">
        <el-table :data="orders" style="width: 100%">
          <el-table-column prop="order_no" label="订单号" width="200" />
          <el-table-column prop="membership_type" label="套餐类型" width="120">
            <template #default="{ row }">
              {{ getMembershipTypeName(row.membership_type) }}
            </template>
          </el-table-column>
          <el-table-column prop="amount" label="支付金额" width="100">
            <template #default="{ row }">￥{{ row.amount }}</template>
          </el-table-column>
          <el-table-column prop="payment_status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag v-if="row.payment_status === 'paid'" type="success">已支付</el-tag>
              <el-tag v-else-if="row.payment_status === 'pending'" type="warning">待支付</el-tag>
              <el-tag v-else type="danger">{{ row.payment_status }}</el-tag>
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
            <span class="order-type">{{ getMembershipTypeName(order.membership_type) }}</span>
            <el-tag v-if="order.payment_status === 'paid'" type="success" size="small">已支付</el-tag>
            <el-tag v-else-if="order.payment_status === 'pending'" type="warning" size="small">待支付</el-tag>
            <el-tag v-else type="danger" size="small">{{ order.payment_status }}</el-tag>
          </div>
          <div class="order-body">
            <div class="info-row">
              <span>支付金额</span>
              <span class="price">￥{{ order.amount }}</span>
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

      <el-empty v-else description="暂无购买记录" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Check, CreditCard, Wallet } from '@element-plus/icons-vue'
import {
  createMembershipOrder,
  getCreditBalance,
  getMembershipOrders,
  getMembershipPrices,
  simulatePayment,
  type CreditBalance,
  type MembershipOrder,
  type MembershipPrice,
} from '@/api/credit'

const balance = ref<CreditBalance>({
  credits: 0,
  is_member: false,
  member_expired_at: null,
})

const prices = ref<MembershipPrice[]>([])
const selectedPrice = ref<MembershipPrice | null>(null)
const paymentMethod = ref('alipay')
const loading = ref(false)
const orders = ref<MembershipOrder[]>([])

const getMembershipTypeName = (type: string) => {
  const names: Record<string, string> = {
    monthly: '月度会员',
    quarterly: '季度会员',
    yearly: '年度会员',
  }
  return names[type] || type
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

const loadPrices = async () => {
  try {
    const response = await getMembershipPrices()
    prices.value = Array.isArray(response.data) ? response.data : (response.data as any)?.items || []
    if (!selectedPrice.value && prices.value.length > 0) {
      selectedPrice.value = prices.value[0]
    }
  } catch (error) {
    console.error('加载会员价格失败:', error)
  }
}

const loadOrders = async () => {
  try {
    const response = await getMembershipOrders({ limit: 10 })
    orders.value = (response.data as any)?.items || response.data || []
  } catch (error) {
    console.error('加载购买记录失败:', error)
  }
}

const selectPrice = (price: MembershipPrice) => {
  selectedPrice.value = price
}

const handlePurchase = async () => {
  if (!selectedPrice.value) {
    ElMessage.warning('请选择会员套餐')
    return
  }

  loading.value = true
  try {
    await createMembershipOrder({
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

const handleSimulatePayment = async (order: MembershipOrder) => {
  try {
    await simulatePayment({
      order_type: 'membership',
      order_no: order.order_no,
    })
    ElMessage.success('支付成功')
    await loadBalance()
    await loadOrders()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.message || '支付失败')
  }
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

  span:last-child {
    color: #64748b;
    font-size: 13px;
    font-weight: 600;
  }
}

.status-info {
  display: flex;
  flex-wrap: wrap;
  gap: 28px;
  margin-top: 18px;
}

.status-item {
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

.benefits-list {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.benefit-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px;
  border-radius: 18px;
  background: rgba(248, 250, 252, 0.9);

  .icon {
    font-size: 22px;
    flex-shrink: 0;
  }

  .title {
    margin-bottom: 4px;
    color: #0f172a;
    font-size: 15px;
    font-weight: 700;
  }

  .desc {
    color: #64748b;
    font-size: 13px;
    line-height: 1.6;
  }
}

.price-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 18px;
}

.price-item {
  position: relative;
  padding: 24px;
  border-radius: 22px;
  border: 1px solid rgba(37, 99, 235, 0.1);
  background: rgba(255, 255, 255, 0.72);
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

  &.recommended {
    border-color: rgba(15, 159, 110, 0.24);
    background: linear-gradient(180deg, rgba(240, 253, 244, 0.92), rgba(255, 255, 255, 0.84));
  }

  .badge {
    position: absolute;
    top: 12px;
    right: 12px;
    padding: 5px 10px;
    border-radius: 999px;
    background: linear-gradient(135deg, #0f9f6e, #34d399);
    color: #fff;
    font-size: 12px;
    font-weight: 700;
    box-shadow: 0 10px 18px rgba(15, 159, 110, 0.16);
  }

  .type {
    margin-bottom: 6px;
    color: #0f172a;
    font-size: 18px;
    font-weight: 700;
  }

  .duration {
    margin-bottom: 12px;
    color: #64748b;
    font-size: 14px;
  }

  .price {
    margin-bottom: 8px;

    .current {
      margin-right: 8px;
      color: #2563eb;
      font-size: 28px;
      font-weight: 700;
    }

    .original {
      color: #94a3b8;
      font-size: 14px;
      text-decoration: line-through;
    }
  }

  .discount {
    margin-bottom: 6px;
    color: #ef4444;
    font-size: 14px;
    font-weight: 700;
  }

  .daily {
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

.original-price {
  color: #94a3b8;
  text-decoration: line-through;
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
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
  }

  .order-type {
    color: #0f172a;
    font-weight: 700;
  }

  .info-row {
    display: flex;
    justify-content: space-between;
    margin-bottom: 8px;
    color: #475569;
    font-size: 14px;

    .price {
      color: #2563eb;
      font-weight: 700;
    }
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

  .benefits-list,
  .price-list {
    grid-template-columns: 1fr;
  }

  .table-view {
    display: none;
  }

  .card-view {
    display: block;
  }
}
</style>
