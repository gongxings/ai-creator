<template>
  <div class="membership-benefits">
    <h2>会员权益</h2>
    <p class="subtitle">选择适合您的会员套餐，享受更多创作权益</p>
    <div class="benefits-grid">
      <el-card
        v-for="plan in membershipPlans"
        :key="plan.type"
        class="benefit-card"
        :class="{ recommended: plan.recommended }"
        shadow="hover"
      >
        <div v-if="plan.recommended" class="recommended-badge">推荐</div>
        <div class="plan-header">
          <h3>{{ plan.name }}</h3>
          <div class="price">
            <span class="amount">¥{{ plan.price }}</span>
            <span class="period">/{{ plan.period }}</span>
          </div>
        </div>
        <ul class="features-list">
          <li v-for="(feature, index) in plan.features" :key="index">
            <el-icon color="#67c23a"><Check /></el-icon>
            <span>{{ feature }}</span>
          </li>
        </ul>
        <el-button
          type="primary"
          :plain="!plan.recommended"
          size="large"
          class="purchase-btn"
          @click="goToPurchase(plan.type)"
        >
          {{ plan.buttonText }}
        </el-button>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Check } from '@element-plus/icons-vue'

const router = useRouter()

const membershipPlans = ref([
  {
    type: 'basic',
    name: '基础会员',
    price: 29,
    period: '月',
    recommended: false,
    buttonText: '立即开通',
    features: [
      '每日50次AI创作',
      '基础写作工具',
      '图片生成（标清）',
      '历史记录保存',
      '基础模板库',
    ],
  },
  {
    type: 'pro',
    name: '专业会员',
    price: 99,
    period: '月',
    recommended: true,
    buttonText: '立即升级',
    features: [
      '每日200次AI创作',
      '全部写作工具',
      '图片生成（高清）',
      '视频生成（标清）',
      'PPT生成',
      '无限历史记录',
      '高级模板库',
      '优先客服支持',
    ],
  },
  {
    type: 'vip',
    name: 'VIP会员',
    price: 299,
    period: '月',
    recommended: false,
    buttonText: '尊享开通',
    features: [
      '无限次AI创作',
      '全部高级功能',
      '图片生成（超清）',
      '视频生成（高清）',
      '多平台一键发布',
      '专属AI模型',
      '定制化服务',
      '专属客服经理',
      '优先新功能体验',
    ],
  },
])

const goToPurchase = (planType: string) => {
  router.push(`/credit/membership?plan=${planType}`)
}
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
