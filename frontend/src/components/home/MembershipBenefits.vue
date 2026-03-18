<template>
  <div class="membership-benefits">
    <h2>会员权益</h2>
    <p class="subtitle">选择适合你的会员方案，获得更完整的创作能力与服务支持。</p>
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="3" animated />
    </div>
    <div v-else class="benefits-grid">
      <el-card
        v-for="plan in membershipPlans"
        :key="plan.id"
        class="benefit-card"
        :class="{ recommended: plan.membership_type === 'yearly' }"
        shadow="hover"
      >
        <div v-if="plan.membership_type === 'yearly'" class="recommended-badge">推荐</div>
        <div class="plan-header">
          <h3>{{ plan.name }}</h3>
          <div class="price">
            <span class="amount">￥{{ plan.amount }}</span>
            <span class="period">/{{ getPeriodText(plan.membership_type) }}</span>
          </div>
          <div v-if="plan.original_amount" class="original-price">原价 ￥{{ plan.original_amount }}</div>
        </div>
        <ul class="features-list">
          <li v-for="(feature, index) in plan.featureList" :key="index">
            <el-icon color="#0f9f6e"><Check /></el-icon>
            <span>{{ feature }}</span>
          </li>
        </ul>
        <el-button
          type="primary"
          :plain="plan.membership_type !== 'yearly'"
          size="large"
          class="purchase-btn"
          @click="goToPurchase(plan.membership_type)"
        >
          {{ plan.membership_type === 'yearly' ? '立即升级' : '立即开通' }}
        </el-button>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { Check } from '@element-plus/icons-vue'
import { getMembershipPrices, type MembershipPrice } from '@/api/credit'

interface MembershipPlan extends MembershipPrice {
  featureList: string[]
}

const router = useRouter()
const loading = ref(true)
const membershipPlans = ref<MembershipPlan[]>([])

const defaultFeatures: Record<string, string[]> = {
  monthly: ['全部 AI 创作工具不限次数', '不消耗积分', '基础客服支持'],
  quarterly: ['全部 AI 创作工具不限次数', '不消耗积分', '优先客服支持', '新功能优先体验'],
  yearly: ['全部 AI 创作工具不限次数', '不消耗积分', '专属客服支持', '新功能优先体验', '更多高级能力开放'],
}

const getPeriodText = (type: string) => {
  const periods: Record<string, string> = {
    monthly: '月',
    quarterly: '季',
    yearly: '年',
  }
  return periods[type] || '月'
}

const loadMembershipPrices = async () => {
  loading.value = true
  try {
    const res = await getMembershipPrices()
    membershipPlans.value = res.data
      .filter((price: MembershipPrice) => price.is_active)
      .sort((a: MembershipPrice, b: MembershipPrice) => (a.sort_order || 0) - (b.sort_order || 0))
      .map((price: MembershipPrice) => {
        let featureList: string[] = []
        if (price.features) {
          try {
            featureList = JSON.parse(price.features)
          } catch {
            featureList = defaultFeatures[price.membership_type] || []
          }
        } else {
          featureList = defaultFeatures[price.membership_type] || []
        }

        return {
          ...price,
          featureList,
        }
      })
  } catch (error) {
    console.error('加载会员价格失败:', error)
    membershipPlans.value = [
      {
        id: 1,
        name: '月度会员',
        membership_type: 'monthly',
        amount: 29,
        original_amount: 39,
        duration_days: 30,
        description: null,
        features: null,
        is_active: true,
        sort_order: 1,
        featureList: defaultFeatures.monthly,
      },
      {
        id: 2,
        name: '季度会员',
        membership_type: 'quarterly',
        amount: 79,
        original_amount: 117,
        duration_days: 90,
        description: null,
        features: null,
        is_active: true,
        sort_order: 2,
        featureList: defaultFeatures.quarterly,
      },
      {
        id: 3,
        name: '年度会员',
        membership_type: 'yearly',
        amount: 299,
        original_amount: 468,
        duration_days: 365,
        description: null,
        features: null,
        is_active: true,
        sort_order: 3,
        featureList: defaultFeatures.yearly,
      },
    ]
  } finally {
    loading.value = false
  }
}

const goToPurchase = (planType: string) => {
  router.push(`/credit/membership?plan=${planType}`)
}

onMounted(() => {
  loadMembershipPrices()
})
</script>

<style scoped lang="scss">
.membership-benefits {
  h2 {
    margin-bottom: 8px;
    text-align: center;
    font-size: 30px;
    font-weight: 700;
    color: #0f172a;
  }

  .subtitle {
    margin-bottom: 32px;
    text-align: center;
    font-size: 16px;
    color: #64748b;
  }
}

.loading-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 32px 0;
}

.benefits-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 22px;
}

.benefit-card {
  position: relative;
  border-radius: 24px;
  border: 1px solid rgba(37, 99, 235, 0.12);
  background: rgba(255, 255, 255, 0.82);
  box-shadow: 0 18px 36px rgba(15, 23, 42, 0.08);
  transition: all 0.25s ease;

  &:hover {
    transform: translateY(-6px);
    box-shadow: 0 24px 42px rgba(37, 99, 235, 0.14);
  }

  :deep(.el-card__body) {
    display: flex;
    flex-direction: column;
    height: 100%;
    padding: 30px 24px;
  }

  &.recommended {
    border-color: rgba(37, 99, 235, 0.28);
    background: linear-gradient(180deg, rgba(239, 246, 255, 0.96), rgba(255, 255, 255, 0.86));
    box-shadow: 0 24px 44px rgba(37, 99, 235, 0.16);
  }
}

.recommended-badge {
  position: absolute;
  top: 16px;
  right: 16px;
  padding: 6px 12px;
  border-radius: 999px;
  background: linear-gradient(135deg, #2563eb 0%, #0ea5e9 55%, #38bdf8 100%);
  color: #fff;
  font-size: 12px;
  font-weight: 700;
  box-shadow: 0 12px 24px rgba(37, 99, 235, 0.18);
}

.plan-header {
  padding-bottom: 22px;
  margin-bottom: 22px;
  border-bottom: 1px solid rgba(37, 99, 235, 0.12);
  text-align: center;

  h3 {
    margin-bottom: 14px;
    color: #0f172a;
    font-size: 24px;
    font-weight: 700;
  }
}

.price {
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 4px;

  .amount {
    color: #2563eb;
    font-size: 38px;
    font-weight: 700;
  }

  .period {
    color: #64748b;
    font-size: 16px;
  }
}

.original-price {
  margin-top: 8px;
  color: #94a3b8;
  font-size: 14px;
  text-decoration: line-through;
}

.features-list {
  flex: 1;
  list-style: none;
  margin: 0 0 24px;
  padding: 0;
  display: grid;
  gap: 10px;

  li {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    color: #475569;
    line-height: 1.6;
  }
}

.purchase-btn {
  width: 100%;
  height: 46px;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 700;
}

@media (max-width: 768px) {
  .benefits-grid {
    grid-template-columns: 1fr;
  }
}
</style>
