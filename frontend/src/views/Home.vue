<template>
  <div class="home">
    <div class="welcome-section">
      <h1>欢迎使用AI创作者平台</h1>
      <p>让AI助力您的创作，一键生成优质内容</p>
    </div>

    <div class="tools-section">
      <h2>创作工具</h2>
      <div class="tools-grid">
        <!-- AI写作工具 -->
        <div class="tool-category">
          <h3><el-icon><Edit /></el-icon> AI写作</h3>
          <div class="tool-cards">
            <el-card
              v-for="tool in writingTools"
              :key="tool.type"
              class="tool-card"
              shadow="hover"
              @click="goToTool('writing', tool.type)"
            >
              <div class="tool-icon">
                <el-icon :size="32"><component :is="tool.icon" /></el-icon>
              </div>
              <div class="tool-info">
                <h4>{{ tool.name }}</h4>
                <p>{{ tool.description }}</p>
              </div>
            </el-card>
          </div>
        </div>

        <!-- 其他创作工具 -->
        <div class="tool-category">
          <h3><el-icon><Picture /></el-icon> 其他工具</h3>
          <div class="tool-cards">
            <el-card
              v-for="tool in otherTools"
              :key="tool.path"
              class="tool-card"
              shadow="hover"
              @click="goToPath(tool.path)"
            >
              <div class="tool-icon">
                <el-icon :size="32"><component :is="tool.icon" /></el-icon>
              </div>
              <div class="tool-info">
                <h4>{{ tool.name }}</h4>
                <p>{{ tool.description }}</p>
              </div>
            </el-card>
          </div>
        </div>
      </div>
    </div>

    <div class="stats-section">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stat-card">
            <el-statistic title="总创作数" :value="stats.totalCreations">
              <template #prefix>
                <el-icon><Document /></el-icon>
              </template>
            </el-statistic>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <el-statistic title="今日创作" :value="stats.todayCreations">
              <template #prefix>
                <el-icon><Calendar /></el-icon>
              </template>
            </el-statistic>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <el-statistic title="已发布" :value="stats.published">
              <template #prefix>
                <el-icon><Upload /></el-icon>
              </template>
            </el-statistic>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <el-statistic title="绑定平台" :value="stats.platforms">
              <template #prefix>
                <el-icon><Link /></el-icon>
              </template>
            </el-statistic>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  Edit,
  Document,
  Notebook,
  Files,
  Promotion,
  Tickets,
  VideoCamera,
  Reading,
  Briefcase,
  Management,
  User,
  School,
  RefreshRight,
  Switch,
  Picture,
  Film,
  Postcard,
  Calendar,
  Upload,
  Link,
} from '@element-plus/icons-vue'

const router = useRouter()

// 写作工具列表
const writingTools = ref([
  {
    type: 'wechat_article',
    name: '公众号文章',
    description: '创作适合微信公众号的优质文章',
    icon: 'Document',
  },
  {
    type: 'xiaohongshu_note',
    name: '小红书笔记',
    description: '生成吸引人的小红书种草笔记',
    icon: 'Notebook',
  },
  {
    type: 'official_document',
    name: '公文写作',
    description: '规范的公文、通知、报告等',
    icon: 'Files',
  },
  {
    type: 'academic_paper',
    name: '论文写作',
    description: '学术论文、研究报告撰写',
    icon: 'Reading',
  },
  {
    type: 'marketing_copy',
    name: '营销文案',
    description: '产品推广、广告文案创作',
    icon: 'Promotion',
  },
  {
    type: 'news_article',
    name: '新闻稿/软文',
    description: '新闻报道、软文推广',
    icon: 'Tickets',
  },
  {
    type: 'video_script',
    name: '短视频脚本',
    description: '抖音、快手等短视频脚本',
    icon: 'VideoCamera',
  },
  {
    type: 'story_novel',
    name: '故事/小说',
    description: '创意故事、小说章节创作',
    icon: 'Reading',
  },
  {
    type: 'business_plan',
    name: '商业计划书',
    description: '商业计划、项目方案撰写',
    icon: 'Briefcase',
  },
  {
    type: 'work_report',
    name: '工作报告',
    description: '工作总结、述职报告等',
    icon: 'Management',
  },
  {
    type: 'resume',
    name: '简历/求职信',
    description: '个人简历、求职信撰写',
    icon: 'User',
  },
  {
    type: 'lesson_plan',
    name: '教案/课件',
    description: '教学教案、课件内容',
    icon: 'School',
  },
  {
    type: 'content_rewrite',
    name: '内容改写',
    description: '改写、扩写、缩写、润色',
    icon: 'RefreshRight',
  },
  {
    type: 'translation',
    name: '多语言翻译',
    description: '多语言内容翻译',
    icon: 'Switch',
  },
])

// 其他工具
const otherTools = ref([
  {
    path: '/image',
    name: '图片生成',
    description: 'AI生成精美图片',
    icon: 'Picture',
  },
  {
    path: '/video',
    name: '视频生成',
    description: 'AI生成创意视频',
    icon: 'Film',
  },
  {
    path: '/ppt',
    name: 'PPT生成',
    description: 'AI生成精美PPT',
    icon: 'Postcard',
  },
])

// 统计数据
const stats = ref({
  totalCreations: 0,
  todayCreations: 0,
  published: 0,
  platforms: 0,
})

const goToTool = (category: string, toolType: string) => {
  router.push(`/${category}/${toolType}`)
}

const goToPath = (path: string) => {
  router.push(path)
}

const loadStats = async () => {
  // TODO: 从API加载统计数据
  stats.value = {
    totalCreations: 128,
    todayCreations: 5,
    published: 86,
    platforms: 4,
  }
}

onMounted(() => {
  loadStats()
})
</script>

<style scoped lang="scss">
.home {
  .welcome-section {
    text-align: center;
    padding: 48px 0;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: #fff;
    border-radius: 8px;
    margin-bottom: 32px;

    h1 {
      font-size: 36px;
      font-weight: 600;
      margin-bottom: 16px;
    }

    p {
      font-size: 18px;
      opacity: 0.9;
    }
  }

  .tools-section {
    margin-bottom: 32px;

    h2 {
      font-size: 24px;
      font-weight: 600;
      margin-bottom: 24px;
      color: #333;
    }

    .tool-category {
      margin-bottom: 32px;

      h3 {
        font-size: 18px;
        font-weight: 600;
        margin-bottom: 16px;
        color: #666;
        display: flex;
        align-items: center;
        gap: 8px;
      }

      .tool-cards {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: 16px;

        .tool-card {
          cursor: pointer;
          transition: all 0.3s;

          &:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
          }

          :deep(.el-card__body) {
            display: flex;
            align-items: center;
            gap: 16px;
            padding: 20px;
          }

          .tool-icon {
            flex-shrink: 0;
            width: 48px;
            height: 48px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: #f5f7fa;
            border-radius: 8px;
            color: #409eff;
          }

          .tool-info {
            flex: 1;

            h4 {
              font-size: 16px;
              font-weight: 600;
              color: #333;
              margin-bottom: 4px;
            }

            p {
              font-size: 14px;
              color: #666;
              margin: 0;
            }
          }
        }
      }
    }
  }

  .stats-section {
    .stat-card {
      text-align: center;

      :deep(.el-statistic) {
        .el-statistic__head {
          font-size: 14px;
          color: #666;
          margin-bottom: 8px;
        }

        .el-statistic__content {
          font-size: 28px;
          font-weight: 600;
          color: #333;
        }
      }
    }
  }
}

@media (max-width: 768px) {
  .home {
    .welcome-section {
      padding: 32px 16px;

      h1 {
        font-size: 28px;
      }

      p {
        font-size: 16px;
      }
    }

    .tools-section {
      .tool-category {
        .tool-cards {
          grid-template-columns: 1fr;
        }
      }
    }

    .stats-section {
      :deep(.el-col) {
        margin-bottom: 16px;
      }
    }
  }
}
</style>
