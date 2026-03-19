<template>
  <div class="writing-tools page-shell">
    <section class="page-hero">
      <div>
        <p class="eyebrow">Writing Workspace</p>
        <h1>AI 写作工具</h1>
        <p class="description">按场景选择合适的写作能力，快速生成更完整、更稳定的内容草稿。</p>
      </div>
    </section>

    <!-- 热点追踪模块 -->
    <HotspotPanel />

    <section class="tools-filter app-panel">
      <el-segmented v-model="activeCategory" :options="categories" block />
    </section>

    <section v-if="recentTools.length > 0" class="recent-section section-block">
      <div class="section-header">
        <div>
          <p class="section-kicker">Recent</p>
          <h3>最近使用</h3>
        </div>
        <el-button text type="primary" @click="clearRecent">清空</el-button>
      </div>
      <div class="tools-grid">
        <el-card
          v-for="tool in recentTools"
          :key="tool.type"
          class="tool-card recent-card"
          shadow="hover"
          @click="goToEditor(tool.type)"
        >
          <div class="badge">最近</div>
          <div class="tool-icon" :style="{ '--tool-color': tool.color }">
            <el-icon :size="30"><component :is="tool.icon" /></el-icon>
          </div>
          <h3>{{ tool.name }}</h3>
          <p>{{ tool.description }}</p>
        </el-card>
      </div>
    </section>

    <section v-if="filteredTools.length > 0" class="tools-section section-block">
      <div class="section-header">
        <div>
          <p class="section-kicker">Library</p>
          <h3>{{ getCategoryTitle(activeCategory) }}</h3>
        </div>
        <span class="count">共 {{ filteredTools.length }} 个工具</span>
      </div>
      <div class="tools-grid">
        <el-card
          v-for="tool in filteredTools"
          :key="tool.type"
          class="tool-card"
          :class="{ 'hot-tool': tool.isHot }"
          shadow="hover"
          @click="goToEditor(tool.type)"
        >
          <div v-if="tool.isHot" class="badge hot">热门</div>
          <div class="tool-icon" :style="{ '--tool-color': tool.color }">
            <el-icon :size="30"><component :is="tool.icon" /></el-icon>
          </div>
          <h3>{{ tool.name }}</h3>
          <p>{{ tool.description }}</p>
          <div class="tool-tags">
            <el-tag v-for="tag in tool.tags" :key="tag" size="small" type="info" effect="plain">
              {{ tag }}
            </el-tag>
          </div>
          <div class="tool-usage">
            <span class="usage-count">{{ tool.usageCount }} 次使用</span>
          </div>
        </el-card>
      </div>
    </section>

    <section v-if="filteredTools.length === 0" class="empty-state app-panel">
      <el-empty description="该分类暂无工具" />
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  Briefcase,
  ChatDotRound,
  Connection,
  DataAnalysis,
  Document,
  Edit,
  Notebook,
  Promotion,
  Reading,
  RefreshRight,
  Tickets,
  TrendCharts,
  User,
  VideoCamera,
} from '@element-plus/icons-vue'
import HotspotPanel from '@/components/hotspot/HotspotPanel.vue'

const router = useRouter()
const activeCategory = ref('all')

const categories = [
  { label: '全部', value: 'all' },
  { label: '自媒体', value: 'social' },
  { label: '专业写作', value: 'professional' },
  { label: '创意内容', value: 'creative' },
  { label: '内容优化', value: 'optimization' },
]

const writingTools = [
  {
    type: 'wechat_article',
    name: '公众号文章',
    description: '适合公众号长文、观点稿和专题内容，兼顾结构和可读性。',
    icon: Document,
    color: '#07C160',
    tags: ['自媒体', '长文'],
    category: 'social',
    isHot: true,
    usageCount: 1245,
  },
  {
    type: 'xiaohongshu_note',
    name: '小红书笔记',
    description: '生成标题、正文和标签，适合种草、攻略与生活方式内容。',
    icon: ChatDotRound,
    color: '#FF2442',
    tags: ['种草', '短文'],
    category: 'social',
    isHot: true,
    usageCount: 2341,
  },
  {
    type: 'official_document',
    name: '公文写作',
    description: '适合通知、报告、函件等正式文稿，强调规范表达。',
    icon: Notebook,
    color: '#409EFF',
    tags: ['正式', '规范'],
    category: 'professional',
    isHot: false,
    usageCount: 523,
  },
  {
    type: 'academic_paper',
    name: '论文写作',
    description: '支持摘要、章节结构和研究型表达，适合学术类内容。',
    icon: Reading,
    color: '#E6A23C',
    tags: ['学术', '专业'],
    category: 'professional',
    isHot: false,
    usageCount: 678,
  },
  {
    type: 'marketing_copy',
    name: '营销文案',
    description: '适配广告、活动和品牌推广场景，突出转化和节奏。',
    icon: Promotion,
    color: '#F56C6C',
    tags: ['营销', '转化'],
    category: 'professional',
    isHot: true,
    usageCount: 1890,
  },
  {
    type: 'news_article',
    name: '新闻软文',
    description: '适合品牌稿、活动报道和新闻型传播内容。',
    icon: Tickets,
    color: '#909399',
    tags: ['新闻', '传播'],
    category: 'professional',
    isHot: false,
    usageCount: 456,
  },
  {
    type: 'video_script',
    name: '短视频脚本',
    description: '生成分镜、口播和镜头节奏，适合短视频内容策划。',
    icon: VideoCamera,
    color: '#67C23A',
    tags: ['视频', '脚本'],
    category: 'social',
    isHot: true,
    usageCount: 1567,
  },
  {
    type: 'story_novel',
    name: '故事小说',
    description: '适合故事设定、情节推进和角色对白创作。',
    icon: Edit,
    color: '#9C27B0',
    tags: ['创意', '文学'],
    category: 'creative',
    isHot: false,
    usageCount: 234,
  },
  {
    type: 'business_plan',
    name: '商业计划书',
    description: '适合商业方案、路演材料和项目推进文档。',
    icon: Briefcase,
    color: '#FF9800',
    tags: ['商业', '专业'],
    category: 'professional',
    isHot: false,
    usageCount: 345,
  },
  {
    type: 'work_report',
    name: '工作报告',
    description: '用于工作总结、周报、月报和述职内容梳理。',
    icon: DataAnalysis,
    color: '#00BCD4',
    tags: ['职场', '总结'],
    category: 'professional',
    isHot: false,
    usageCount: 789,
  },
  {
    type: 'resume',
    name: '简历求职',
    description: '用于简历、自我介绍和求职材料优化。',
    icon: User,
    color: '#4CAF50',
    tags: ['求职', '简历'],
    category: 'professional',
    isHot: false,
    usageCount: 632,
  },
  {
    type: 'content_rewrite',
    name: '内容改写',
    description: '支持改写、扩写、压缩和风格调整。',
    icon: RefreshRight,
    color: '#795548',
    tags: ['改写', '优化'],
    category: 'optimization',
    isHot: true,
    usageCount: 983,
  },
  {
    type: 'translation',
    name: '多语翻译',
    description: '适合跨语言内容转换和语义优化。',
    icon: Connection,
    color: '#3F51B5',
    tags: ['翻译', '多语'],
    category: 'optimization',
    isHot: false,
    usageCount: 417,
  },
  {
    type: 'viral_analyze',
    name: '爆款分析',
    description: '深度拆解爆款文章的成功要素，提取写作技巧和爆款元素。',
    icon: DataAnalysis,
    color: '#9C27B0',
    tags: ['爆款', '分析'],
    category: 'creative',
    isHot: true,
    usageCount: 0,
  },
  {
    type: 'viral_imitate',
    name: '爆款模仿',
    description: '参考爆款文章风格，围绕新主题生成类似风格内容。',
    icon: TrendCharts,
    color: '#E91E63',
    tags: ['爆款', '模仿'],
    category: 'creative',
    isHot: true,
    usageCount: 0,
  },
]

const recentTools = ref<typeof writingTools>([])

onMounted(() => {
  const recent = localStorage.getItem('recentTools') || '[]'
  const recentIds = JSON.parse(recent) as string[]
  recentTools.value = recentIds
    .map((id) => writingTools.find((tool) => tool.type === id))
    .filter((tool): tool is (typeof writingTools)[number] => Boolean(tool))
      .slice(0, 4)
})

const filteredTools = computed(() => {
  let filtered = writingTools

  if (activeCategory.value !== 'all') {
    filtered = filtered.filter((tool) => tool.category === activeCategory.value)
  }

  return filtered.sort((a, b) => {
    if (a.isHot !== b.isHot) return a.isHot ? -1 : 1
    return b.usageCount - a.usageCount
  })
})

const goToEditor = (toolType: string) => {
  let recent = localStorage.getItem('recentTools') || '[]'
  let recentIds = JSON.parse(recent) as string[]
  recentIds = recentIds.filter((id) => id !== toolType)
  recentIds.unshift(toolType)
  localStorage.setItem('recentTools', JSON.stringify(recentIds.slice(0, 5)))
  router.push(`/writing/${toolType}`)
}

const getCategoryTitle = (category: string) => {
  return categories.find((item) => item.value === category)?.label || '全部工具'
}

const clearRecent = () => {
  localStorage.removeItem('recentTools')
  recentTools.value = []
}
</script>

<style scoped lang="scss">
.page-shell {
  display: flex;
  flex-direction: column;
  gap: 22px;
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

.tools-filter {
  display: flex;
  gap: 16px;
  align-items: center;
  flex-wrap: wrap;
  padding: 18px;

  :deep(.el-segmented) {
    padding: 4px;
    border-radius: 14px;
    background: rgba(241, 245, 249, 0.9);

    .el-segmented__group {
      .el-segmented__item {
        min-width: 90px !important;
        padding: 8px 20px !important;
      }

      .el-segmented__item-label {
        min-width: 60px;
        white-space: nowrap;
      }
    }
  }
}

.section-block {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.section-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16px;

  h3 {
    margin: 0;
    font-size: 24px;
    color: #0f172a;
  }

  .count {
    color: #64748b;
    font-size: 14px;
    font-weight: 600;
  }
}

.section-kicker {
  margin-bottom: 6px;
  color: #2563eb;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.tools-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 18px;
}

.tool-card {
  position: relative;
  cursor: pointer;
  border-radius: 24px;
  border: 1px solid rgba(37, 99, 235, 0.12);
  background: rgba(255, 255, 255, 0.82);
  box-shadow: 0 16px 36px rgba(15, 23, 42, 0.08);
  backdrop-filter: blur(14px);
  transition: all 0.25s ease;

  &:hover {
    transform: translateY(-6px);
    box-shadow: 0 24px 42px rgba(37, 99, 235, 0.14);
    border-color: rgba(37, 99, 235, 0.2);
  }

  &.hot-tool {
    background: linear-gradient(180deg, rgba(255, 251, 235, 0.9), rgba(255, 255, 255, 0.88));
    border-color: rgba(245, 158, 11, 0.22);
  }

  &.recent-card {
    background: linear-gradient(180deg, rgba(239, 246, 255, 0.92), rgba(255, 255, 255, 0.88));
  }

  :deep(.el-card__body) {
    padding: 20px;
    text-align: center;
  }

  .badge {
    position: absolute;
    top: 14px;
    right: 14px;
    padding: 5px 10px;
    border-radius: 999px;
    background: rgba(148, 163, 184, 0.14);
    color: #475569;
    font-size: 12px;
    font-weight: 700;

    &.hot {
      background: linear-gradient(135deg, #f59e0b, #fbbf24);
      color: #fff;
      box-shadow: 0 10px 18px rgba(245, 158, 11, 0.22);
    }
  }

  .tool-icon {
    width: 60px;
    height: 60px;
    margin: 0 auto 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 18px;
    color: var(--tool-color);
    background: color-mix(in srgb, var(--tool-color) 14%, #ffffff);
    box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.5);
  }

  h3 {
    margin-bottom: 8px;
    font-size: 17px;
    font-weight: 700;
    color: #0f172a;
  }

  p {
    min-height: 44px;
    margin-bottom: 14px;
    color: #64748b;
    font-size: 14px;
    line-height: 1.6;
  }

  .tool-tags {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 12px;
  }

  .tool-usage {
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px solid rgba(37, 99, 235, 0.08);
    color: #94a3b8;
    font-size: 12px;
  }
}

.empty-state {
  padding: 40px 20px;
  text-align: center;
}

@media (max-width: 768px) {
  .page-hero {
    padding: 28px 22px;

    h1 {
      font-size: 28px;
    }
  }

  .tools-filter {
    flex-direction: column;
    align-items: stretch;

    :deep(.el-segmented) {
      width: 100%;
    }
  }

  .section-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .tools-grid {
    grid-template-columns: 1fr;
  }
}
</style>
