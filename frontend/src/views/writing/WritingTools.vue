<template>
  <div class="writing-tools">
    <div class="page-header">
      <h1>AI写作工具</h1>
      <p>选择适合你的写作场景，一键生成高质量内容</p>
    </div>

    <div class="tools-grid">
      <el-card
        v-for="tool in writingTools"
        :key="tool.type"
        class="tool-card"
        shadow="hover"
        @click="goToEditor(tool.type)"
      >
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
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
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

const writingTools = [
  {
    type: 'wechat_article',
    name: '公众号文章',
    description: '创作适合微信公众号的优质文章，自动优化排版和SEO',
    icon: Document,
    color: '#07C160',
    tags: ['自媒体', '长文'],
  },
  {
    type: 'xiaohongshu_note',
    name: '小红书笔记',
    description: '生成吸引眼球的小红书笔记，包含标题、正文和标签',
    icon: ChatDotRound,
    color: '#FF2442',
    tags: ['种草', '短文'],
  },
  {
    type: 'official_document',
    name: '公文写作',
    description: '规范的公文格式，适用于通知、报告、函件等',
    icon: Notebook,
    color: '#409EFF',
    tags: ['正式', '规范'],
  },
  {
    type: 'academic_paper',
    name: '论文写作',
    description: '学术论文辅助写作，包含摘要、正文、参考文献',
    icon: Reading,
    color: '#E6A23C',
    tags: ['学术', '专业'],
  },
  {
    type: 'marketing_copy',
    name: '营销文案',
    description: '打动人心的营销文案，提升转化率',
    icon: Promotion,
    color: '#F56C6C',
    tags: ['营销', '转化'],
  },
  {
    type: 'news_article',
    name: '新闻稿/软文',
    description: '专业的新闻稿和软文写作，传播品牌价值',
    icon: Tickets,
    color: '#909399',
    tags: ['新闻', '传播'],
  },
  {
    type: 'video_script',
    name: '短视频脚本',
    description: '抖音、快手等短视频脚本，包含分镜和台词',
    icon: VideoCamera,
    color: '#67C23A',
    tags: ['视频', '脚本'],
  },
  {
    type: 'story_novel',
    name: '故事/小说',
    description: '创意故事和小说创作，激发想象力',
    icon: Edit,
    color: '#9C27B0',
    tags: ['创意', '文学'],
  },
  {
    type: 'business_plan',
    name: '商业计划书',
    description: '专业的商业计划书，助力融资和项目推进',
    icon: Briefcase,
    color: '#FF9800',
    tags: ['商业', '专业'],
  },
  {
    type: 'work_report',
    name: '工作报告',
    description: '工作总结、述职报告等，条理清晰',
    icon: DataAnalysis,
    color: '#00BCD4',
    tags: ['职场', '总结'],
  },
  {
    type: 'resume',
    name: '简历/求职信',
    description: '专业的简历和求职信，提升求职成功率',
    icon: User,
    color: '#3F51B5',
    tags: ['求职', '个人'],
  },
  {
    type: 'lesson_plan',
    name: '教案/课件',
    description: '教学教案和课件内容，结构完整',
    icon: Reading,
    color: '#8BC34A',
    tags: ['教育', '教学'],
  },
  {
    type: 'content_rewrite',
    name: '改写/扩写/缩写',
    description: '对现有内容进行改写、扩写或缩写',
    icon: RefreshRight,
    color: '#607D8B',
    tags: ['优化', '改写'],
  },
  {
    type: 'translation',
    name: '多语言翻译',
    description: '支持多种语言互译，保持原文风格',
    icon: Connection,
    color: '#795548',
    tags: ['翻译', '多语言'],
  },
]

const goToEditor = (toolType: string) => {
  router.push(`/writing/${toolType}`)
}
</script>

<style scoped lang="scss">
.writing-tools {
  background: linear-gradient(180deg, #f8fbff 0%, #ffffff 36%);

  .page-header {
    margin-bottom: 24px;
    padding: 24px;
    border-radius: 14px;
    background: linear-gradient(135deg, #eff6ff 0%, #f5f3ff 100%);

    h1 {
      font-size: 30px;
      font-weight: 600;
      color: #111827;
      margin-bottom: 8px;
    }

    p {
      font-size: 14px;
      color: #64748b;
      margin: 0;
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

      &:hover {
        transform: translateY(-5px);
        box-shadow: 0 14px 28px rgba(37, 99, 235, 0.14);
        border-color: #93c5fd;
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
      }
    }
  }
}

@media (max-width: 768px) {
  .writing-tools {
    .page-header {
      padding: 18px;

      h1 {
        font-size: 24px;
      }
    }

    .tools-grid {
      grid-template-columns: 1fr;
    }
  }
}
</style>
