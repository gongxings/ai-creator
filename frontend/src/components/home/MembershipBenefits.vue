<template>
  <div class="membership-benefits">
    <h2>会员权益</h2>
    <p class="subtitle">选择适合您的会员套餐，享受更多创作权益</p>
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
            <span class="amount">¥{{ plan.amount }}</span>
            <span class="period">/{{ getPeriodText(plan.membership_type) }}</span>
          </div>
          <div v-if="plan.original_amount" class="original-price">
            原价 ¥{{ plan.original_amount }}
          </div>
        </div>
        <ul class="features-list">
          <li v-for="(feature, index) in plan.featureList" :key="index">
            <el-icon color="#67c23a"><Check /></el-icon>
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
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Check } from '@element-plus/icons-vue'
import { getMembershipPrices, type MembershipPrice } from '@/api/credit'

interface MembershipPlan extends MembershipPrice {
  featureList: string[]
}

const router = useRouter()
const loading = ref(true)
const membershipPlans = ref<MembershipPlan[]>([])

// 默认权益（当数据库没有配置时使用）
const defaultFeatures: Record<string, string[]> = {
  monthly: ['所有AI创作工具不限次数', '不消耗积分', '基础客服支持'],
  quarterly: ['所有AI创作工具不限次数', '不消耗积分', '优先客服支持', '新功能优先体验'],
  yearly: ['所有AI创作工具不限次数', '不消耗积分', '专属客服经理', '新功能优先体验', '定制化服务支持']
}

const getPeriodText = (type: string) => {
  const periods: Record<string, string> = {
    monthly: '月',
    quarterly: '季',
    yearly: '年'
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
        
        // 尝试解析 features JSON
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
          featureList
        }
      })
  } catch (error) {
    console.error('加载会员价格失败:', error)
    // 使用默认数据
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
        featureList: defaultFeatures.monthly
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
        featureList: defaultFeatures.quarterly
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
        featureList: defaultFeatures.yearly
      }
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
  margin-bottom: 48px;

  h2 {
    font-size: 28px;
    font-weight: 600;
    text-align: center;
    margin-bottom: 8px;
    color: #333;
  }

  .subtitle {
    text-align: center;
    font-size: 16px;
    color: #666;
    margin-bottom: 32px;
  }

  .loading-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 40px;
  }

  .benefits-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 24px;
    max-width: 1200px;
    margin: 0 auto;

    .benefit-card {
      position: relative;
      transition: all 0.3s;
      border: 2px solid transparent;
      display: flex;
      flex-direction: column;
      height: 100%;

      &.recommended {
        border-color: #409eff;
        transform: scale(1.05);

        .recommended-badge {
          position: absolute;
          top: -12px;
          right: 20px;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: #fff;
          padding: 4px 16px;
          border-radius: 12px;
          font-size: 12px;
          font-weight: 600;
        }
      }

      &:hover {
        transform: translateY(-8px);
        box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
      }

      :deep(.el-card__body) {
        padding: 32px 24px;
        display: flex;
        flex-direction: column;
        height: 100%;
      }

      .plan-header {
        text-align: center;
        margin-bottom: 24px;
        padding-bottom: 24px;
        border-bottom: 1px solid #eee;

        h3 {
          font-size: 24px;
          font-weight: 600;
          color: #333;
          margin-bottom: 16px;
        }

        .price {
          display: flex;
          align-items: baseline;
          justify-content: center;
          gap: 4px;

          .amount {
            font-size: 36px;
            font-weight: 700;
            color: #409eff;
          }

          .period {
            font-size: 16px;
            color: #666;
          }
        }
        
        .original-price {
          font-size: 14px;
          color: #999;
          text-decoration: line-through;
          margin-top: 8px;
        }
      }

      .features-list {
        list-style: none;
        padding: 0;
        margin: 0 0 24px 0;
        flex: 1;

        li {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 8px 0;
          font-size: 14px;
          color: #666;

          .el-icon {
            flex-shrink: 0;
          }

          span {
            flex: 1;
          }
        }
      }

      .purchase-btn {
        width: 100%;
        font-size: 16px;
        font-weight: 600;
        height: 44px;
      }
    }
  }
}

@media (max-width: 768px) {
  .membership-benefits {
    .benefits-grid {
      grid-template-columns: 1fr;

      .benefit-card {
        &.recommended {
          transform: scale(1);
        }
      }
    }
  }
}
</style>
