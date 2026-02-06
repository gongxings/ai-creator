<template>
  <div class="writing-tools flagship-page page-shell">
    <section class="page-hero writing-hero">
      <div class="hero-grid">
        <div class="hero-main">
          <span class="hero-eyebrow">Writing Lab</span>
          <h1 class="hero-title">AI写作工具</h1>
          <p class="hero-subtitle">选择适合你的写作场景，一键生成高质量内容。</p>
          <div class="hero-actions">
            <el-button type="primary" @click="resetFilter">重置筛选</el-button>
            <el-button :disabled="recentTools.length === 0" @click="clearRecent">清空最近</el-button>
          </div>
        </div>
        <div class="hero-panel">
          <div class="hero-panel-title">工具概览</div>
          <div class="hero-stats">
            <div class="hero-stat">
              <div class="hero-stat-value">{{ writingTools.length }}</div>
              <div class="hero-stat-label">工具数量</div>
            </div>
            <div class="hero-stat">
              <div class="hero-stat-value">{{ filteredTools.length }}</div>
              <div class="hero-stat-label">当前结果</div>
            </div>
            <div class="hero-stat">
              <div class="hero-stat-value">{{ recentTools.length }}</div>
              <div class="hero-stat-label">最近使用</div>
            </div>
            <div class="hero-stat">
              <div class="hero-stat-value">{{ categories.length - 1 }}</div>
              <div class="hero-stat-label">内容场景</div>
            </div>
          </div>
          <div class="hero-tags">
            <span v-for="item in categories" :key="item.value" class="hero-tag">{{ item.label }}</span>
          </div>
        </div>
      </div>
    </section>

    <section class="page-dashboard">
      <div class="dashboard-grid">
        <div class="dashboard-card">
          <div class="label">当前分类</div>
          <div class="value">{{ getCategoryTitle(activeCategory) }}</div>
          <div class="delta">快速定位最匹配场景</div>
        </div>
        <div class="dashboard-card">
          <div class="label">匹配工具</div>
          <div class="value">{{ filteredTools.length }}</div>
          <div class="delta">按热度自动排序</div>
        </div>
        <div class="dashboard-card">
          <div class="label">热门标签</div>
          <div class="value">转化 / SEO</div>
          <div class="delta">更贴近需求表达</div>
        </div>
      </div>
    </section>

    <section class="page-body">
      <div class="main-panel">
        <div class="panel tools-filter-panel">
          <div class="tools-filter">
            <el-input
              v-model="searchQuery"
              placeholder="搜索工具..."
              prefix-icon="Search"
              class="search-box"
              clearable
            />
            <el-segmented
              v-model="activeCategory"
              :options="categories"
              block
            />
          </div>
        </div>

        <div v-if="recentTools.length > 0" class="panel recent-section">
          <div class="section-header">
            <h3>最近使用</h3>
            <el-button type="text" @click="clearRecent">清空</el-button>
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
                <el-icon :size="30">
                  <component :is="tool.icon" />
                </el-icon>
              </div>
              <h3>{{ tool.name }}</h3>
              <p>{{ tool.description }}</p>
            </el-card>
          </div>
        </div>

        <div v-if="filteredTools.length > 0" class="panel tools-section">
          <div class="section-header">
            <h3>{{ getCategoryTitle(activeCategory) }}</h3>
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
                <el-icon :size="30">
                  <component :is="tool.icon" />
                </el-icon>
              </div>
              <h3>{{ tool.name }}</h3>
              <p>{{ tool.description }}</p>
              <div class="tool-tags">
                <el-tag
                  v-for="tag in tool.tags"
                  :key="tag"
                  size="small"
                  type="info"
                  effect="plain"
                >
                  {{ tag }}
                </el-tag>
              </div>
              <div class="tool-usage">
                <span class="usage-count">{{ tool.usageCount }} 次使用</span>
              </div>
            </el-card>
          </div>
        </div>

        <div v-else class="panel empty-state">
          <el-empty description="未找到匹配的工具" />
          <el-button type="primary" @click="resetFilter">重置筛选</el-button>
        </div>
      </div>

      <aside class="side-panel">
        <div class="panel">
          <h3 class="panel-title">写作加速器</h3>
          <p class="panel-subtitle">三步进入高效创作流程</p>
          <div class="info-list">
            <div class="info-item">
              <div class="info-icon"><el-icon><Document /></el-icon></div>
              <div>
                <div class="info-title">明确主题</div>
                <div class="info-desc">聚焦你的受众与场景，快速锁定方向。</div>
              </div>
            </div>
            <div class="info-item">
              <div class="info-icon"><el-icon><Edit /></el-icon></div>
              <div>
                <div class="info-title">补充关键词</div>
                <div class="info-desc">关键卖点与语气决定内容质感。</div>
              </div>
            </div>
            <div class="info-item">
              <div class="info-icon"><el-icon><Promotion /></el-icon></div>
              <div>
                <div class="info-title">一键发布</div>
                <div class="info-desc">生成后可直接进入发布管理。</div>
              </div>
            </div>
          </div>
        </div>

        <div class="panel">
          <h3 class="panel-title">热门场景</h3>
          <div class="hero-tags">
            <span v-for="tool in writingTools.slice(0, 6)" :key="tool.type" class="hero-tag">{{ tool.name }}</span>
          </div>
        </div>
      </aside>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Search } from '@element-plus/icons-vue'
import {
  Document,
  ChatDotRound,
  Promotion,
  Reading,
  Notebook,
  VideoCamera,
  Tickets,
  Briefcase,
  DataAnalysis,
  User,
  Edit,
  RefreshRight,
  Connection,
} from '@element-plus/icons-vue'

const router = useRouter()
const searchQuery = ref('')
const activeCategory = ref('all')

const categories = [
  { label: '全部', value: 'all' },
  { label: '自媒体', value: 'social' },
  { label: '专业写作', value: 'professional' },
  { label: '创意创作', value: 'creative' },
  { label: '内容优化', value: 'optimization' },
]

const writingTools = [
  {
    type: 'wechat_article',
    name: '公众号文章',
    description: '创作适合微信公众号的优质文章，自动优化排版和SEO',
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
    description: '生成吸引眼球的小红书笔记，包含标题、正文和标签',
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
    description: '规范的公文格式，适用于通知、报告、函件等',
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
    description: '学术论文辅助写作，包含摘要、正文、参考文献',
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
    description: '打动人心的营销文案，提升转化率',
    icon: Promotion,
    color: '#F56C6C',
    tags: ['营销', '转化'],
    category: 'professional',
    isHot: true,
    usageCount: 1890,
  },
  {
    type: 'news_article',
    name: '新闻稿/软文',
    description: '专业的新闻稿和软文写作，传播品牌价值',
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
    description: '抖音、快手等短视频脚本，包含分镜和台词',
    icon: VideoCamera,
    color: '#67C23A',
    tags: ['视频', '脚本'],
    category: 'social',
    isHot: true,
    usageCount: 1567,
  },
  {
    type: 'story_novel',
    name: '故事/小说',
    description: '创意故事和小说创作，激发想象力',
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
    description: '专业的商业计划书，助力融资和项目推进',
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
    description: '工作总结、述职报告等，条理清晰',
    icon: DataAnalysis,
    color: '#00BCD4',
    tags: ['职场', '总结'],
    category: 'professional',
    isHot: false,
    usageCount: 789,
  },
  {
    type: 'resume',
    name: '简历/求职信',
    description: '专业的简历和求职信，提升求职成功率',
    icon: User,
    color: '#3F51B5',
    tags: ['求职', '个人'],
    category: 'professional',
    isHot: false,
    usageCount: 1123,
  },
  {
    type: 'lesson_plan',
    name: '教案/课件',
    description: '教学教案和课件内容，结构完整',
    icon: Reading,
    color: '#8BC34A',
    tags: ['教育', '教学'],
    category: 'professional',
    isHot: false,
    usageCount: 267,
  },
  {
    type: 'content_rewrite',
    name: '改写/扩写/缩写',
    description: '对现有内容进行改写、扩写或缩写',
    icon: RefreshRight,
    color: '#607D8B',
    tags: ['优化', '改写'],
    category: 'optimization',
    isHot: false,
    usageCount: 2156,
  },
  {
    type: 'translation',
    name: '多语言翻译',
    description: '支持多种语言互译，保持原文风格',
    icon: Connection,
    color: '#795548',
    tags: ['翻译', '多语言'],
    category: 'optimization',
    isHot: false,
    usageCount: 876,
  },
]

const recentTools = computed(() => {
  const recent = localStorage.getItem('recentTools')
  if (!recent) return []
  const recentIds = JSON.parse(recent) as string[]
  return recentIds.slice(0, 3).map(id => writingTools.find(t => t.type === id)).filter(Boolean)
})

const filteredTools = computed(() => {
  let filtered = writingTools
  
  // 分类筛选
  if (activeCategory.value !== 'all') {
    filtered = filtered.filter(tool => tool.category === activeCategory.value)
  }
  
  // 搜索筛选
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(tool =>
      tool.name.toLowerCase().includes(query) ||
      tool.description.toLowerCase().includes(query) ||
      tool.tags.some(tag => tag.toLowerCase().includes(query))
    )
  }
  
  return filtered.sort((a, b) => {
    // 热门工具优先
    if (a.isHot !== b.isHot) return a.isHot ? -1 : 1
    // 按使用次数排序
    return b.usageCount - a.usageCount
  })
})

const goToEditor = (toolType: string) => {
  // 保存最近使用
  let recent = localStorage.getItem('recentTools') || '[]'
  let recentIds = JSON.parse(recent) as string[]
  recentIds = recentIds.filter(id => id !== toolType)
  recentIds.unshift(toolType)
  localStorage.setItem('recentTools', JSON.stringify(recentIds.slice(0, 5)))
  
  router.push(`/writing/${toolType}`)
}

const getCategoryTitle = (category: string) => {
  return categories.find(c => c.value === category)?.label || '全部'
}

const resetFilter = () => {
  searchQuery.value = ''
  activeCategory.value = 'all'
}

const clearRecent = () => {
  localStorage.removeItem('recentTools')
}
</script>

<style scoped lang="scss">
.writing-tools {
  background: linear-gradient(180deg, #f8fbff 0%, #ffffff 36%);
  --hero-from: rgba(14, 165, 233, 0.18);
  --hero-to: rgba(99, 102, 241, 0.18);
  --page-accent: #0ea5e9;

  .tools-filter-panel {
    padding: 16px 18px;
  }

  .tools-filter {
    display: flex;
    gap: 16px;
    align-items: center;
    flex-wrap: wrap;

    .search-box {
      flex: 1;
      min-width: 200px;
    }

    :deep(.el-segmented) {
      flex-wrap: wrap;
    }
  }

  .recent-section,
  .tools-section {
    .section-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;

      h3 {
        font-size: 18px;
        font-weight: 600;
        color: #1f2937;
        margin: 0;
      }

      .count {
        font-size: 14px;
        color: #64748b;
      }
    }
  }

  .tools-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
    gap: 18px;

    .tool-card {
      cursor: pointer;
      transition: all 0.3s;
      border: 1px solid #e5e7eb;
      border-radius: 14px;
      position: relative;

      &:hover {
        transform: translateY(-5px);
        box-shadow: 0 14px 28px rgba(37, 99, 235, 0.14);
        border-color: #93c5fd;
      }

      &.hot-tool {
        border-color: #fbbf24;
        background: linear-gradient(135deg, #fffbeb 0%, #fff8e1 100%);
      }

      &.recent-card {
        border-color: #dbeafe;
        background: linear-gradient(135deg, #eff6ff 0%, #f0f9ff 100%);
      }

      .badge {
        position: absolute;
        top: 12px;
        right: 12px;
        font-size: 12px;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 6px;
        background: #f3f4f6;
        color: #6b7280;

        &.hot {
          background: #fbbf24;
          color: #78350f;
        }
      }

      :deep(.el-card__body) {
        padding: 20px;
        text-align: center;
      }

      .tool-icon {
        width: 58px;
        height: 58px;
        margin: 0 auto 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 14px;
        color: var(--tool-color);
        background: color-mix(in srgb, var(--tool-color) 12%, #ffffff);
      }

      h3 {
        font-size: 17px;
        font-weight: 600;
        color: #1f2937;
        margin-bottom: 8px;
      }

      p {
        font-size: 14px;
        color: #64748b;
        line-height: 1.6;
        margin-bottom: 14px;
        min-height: 44px;
      }

      .tool-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        justify-content: center;
        margin-bottom: 12px;
      }

      .tool-usage {
        font-size: 12px;
        color: #9ca3af;
        border-top: 1px solid #e5e7eb;
        padding-top: 12px;
        margin-top: 12px;

        .usage-count {
          display: inline-block;
        }
      }
    }
  }

  .empty-state {
    text-align: center;
    padding: 40px 20px;

    :deep(.el-empty__image) {
      height: 180px;
    }

    :deep(.el-empty__description) {
      margin-bottom: 16px;
    }
  }
}

@media (max-width: 768px) {
  .writing-tools {
    .tools-filter {
      flex-direction: column;

      .search-box {
        width: 100%;
      }

      :deep(.el-segmented) {
        width: 100%;
      }
    }

    .tools-grid {
      grid-template-columns: 1fr;
    }
  }
}
</style>
