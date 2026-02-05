<template>
  <div class="tools-section">
    <h2>创作工具</h2>
    <p class="subtitle">选择适合您的创作工具，快速生成优质内容</p>
    
    <!-- AI写作工具 -->
    <div class="tool-category">
      <h3><el-icon><Edit /></el-icon> AI写作工具</h3>
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
      <h3><el-icon><Picture /></el-icon> 其他创作工具</h3>
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
</template>

<script setup lang="ts">
import { ref } from 'vue'
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

const goToTool = (category: string, toolType: string) => {
  router.push(`/${category}/${toolType}`)
}

const goToPath = (path: string) => {
  router.push(path)
}
</script>

<style scoped lang="scss">
.tools-section {
  padding: 8px 0 4px;
  h2 {
    font-size: 30px;
    font-weight: 600;
    text-align: center;
    margin-bottom: 8px;
    color: #111827;
  }

  .subtitle {
    text-align: center;
    font-size: 16px;
    color: #64748b;
    margin-bottom: 36px;
  }

  .tool-category {
    margin-bottom: 48px;

    &:last-child {
      margin-bottom: 0;
    }

    h3 {
      font-size: 20px;
      font-weight: 600;
      margin-bottom: 24px;
      color: #1f2937;
      display: flex;
      align-items: center;
      gap: 8px;
      padding-left: 8px;
      border-left: 4px solid #2563eb;
    }

    .tool-cards {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
      gap: 20px;

      .tool-card {
        cursor: pointer;
        transition: all 0.3s;
        border: 1px solid #e5e7eb;
        border-radius: 14px;

        &:hover {
          transform: translateY(-6px);
          box-shadow: 0 16px 30px rgba(37, 99, 235, 0.16);
          border-color: #2563eb;

          .tool-icon {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #fff;
          }
        }

        :deep(.el-card__body) {
          display: flex;
          align-items: center;
          gap: 16px;
          padding: 20px;
        }

        .tool-icon {
          flex-shrink: 0;
          width: 56px;
          height: 56px;
          display: flex;
          align-items: center;
          justify-content: center;
          background: linear-gradient(135deg, #f8fafc 0%, #eef2ff 100%);
          border-radius: 12px;
          color: #2563eb;
          transition: all 0.3s;
        }

        .tool-info {
          flex: 1;

          h4 {
            font-size: 16px;
            font-weight: 600;
            color: #333;
            margin-bottom: 6px;
          }

          p {
            font-size: 14px;
            color: #64748b;
            margin: 0;
            line-height: 1.5;
          }
        }
      }
    }
  }
}

@media (max-width: 768px) {
  .tools-section {
    padding: 8px 0 4px;
    .tool-category {
      .tool-cards {
        grid-template-columns: 1fr;
      }
    }
  }
}
</style>
