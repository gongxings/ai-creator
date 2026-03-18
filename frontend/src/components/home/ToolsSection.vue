<template>
  <div class="tools-section">
    <h2>创作工具</h2>
    <p class="subtitle">选择适合你的工具，快速生成高质量内容。</p>

    <div class="tool-category">
      <h3><el-icon><Edit /></el-icon> AI 写作工具</h3>
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
  Briefcase,
  Edit,
  Film,
  Files,
  Management,
  Notebook,
  Picture,
  Postcard,
  Promotion,
  Reading,
  RefreshRight,
  School,
  Switch,
  Tickets,
  User,
  VideoCamera,
} from '@element-plus/icons-vue'

const router = useRouter()

const writingTools = ref([
  { type: 'wechat_article', name: '公众号文章', description: '生成适合公众号的高质量文章内容', icon: 'Document' },
  { type: 'xiaohongshu_note', name: '小红书笔记', description: '快速产出种草风格内容和标题', icon: 'Notebook' },
  { type: 'official_document', name: '公文写作', description: '规范生成通知、报告和制度文稿', icon: 'Files' },
  { type: 'academic_paper', name: '论文写作', description: '辅助产出论文框架和研究型内容', icon: 'Reading' },
  { type: 'marketing_copy', name: '营销文案', description: '生成广告、活动和产品推广文案', icon: 'Promotion' },
  { type: 'news_article', name: '新闻软文', description: '用于新闻稿、品牌稿和活动报道', icon: 'Tickets' },
  { type: 'video_script', name: '短视频脚本', description: '适配短视频平台的脚本和分镜文案', icon: 'VideoCamera' },
  { type: 'story_novel', name: '故事小说', description: '创作故事设定、章节内容和对白', icon: 'Reading' },
  { type: 'business_plan', name: '商业计划书', description: '输出商业方案、路演提纲和计划书', icon: 'Briefcase' },
  { type: 'work_report', name: '工作报告', description: '适合工作总结、述职和复盘材料', icon: 'Management' },
  { type: 'resume', name: '简历求职', description: '撰写简历、求职信和岗位匹配内容', icon: 'User' },
  { type: 'lesson_plan', name: '教案课件', description: '辅助生成教学教案和课程提纲', icon: 'School' },
  { type: 'content_rewrite', name: '内容改写', description: '支持改写、扩写、缩写和润色', icon: 'RefreshRight' },
  { type: 'translation', name: '多语言翻译', description: '完成多语言内容翻译和表达优化', icon: 'Switch' },
])

const otherTools = ref([
  { path: '/image', name: '图片生成', description: 'AI 生成风格化图片与视觉素材', icon: 'Picture' },
  { path: '/video', name: '视频生成', description: 'AI 生成创意视频与配套素材', icon: 'Film' },
  { path: '/ppt', name: 'PPT 生成', description: 'AI 生成结构完整的演示内容', icon: 'Postcard' },
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
  padding: 4px 0 8px;

  h2 {
    margin-bottom: 8px;
    text-align: center;
    font-size: 30px;
    font-weight: 700;
    color: #0f172a;
  }

  .subtitle {
    margin-bottom: 34px;
    text-align: center;
    font-size: 16px;
    color: #64748b;
  }
}

.tool-category {
  margin-bottom: 42px;

  &:last-child {
    margin-bottom: 0;
  }

  h3 {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 22px;
    padding: 10px 16px;
    border-radius: 999px;
    background: rgba(37, 99, 235, 0.08);
    color: #1d4ed8;
    font-size: 18px;
    font-weight: 700;
  }
}

.tool-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 18px;
}

.tool-card {
  cursor: pointer;
  border-radius: 22px;
  border: 1px solid rgba(37, 99, 235, 0.12);
  background: rgba(255, 255, 255, 0.82);
  box-shadow: 0 16px 34px rgba(15, 23, 42, 0.08);
  backdrop-filter: blur(14px);
  transition: all 0.25s ease;

  &:hover {
    transform: translateY(-6px);
    border-color: rgba(37, 99, 235, 0.22);
    box-shadow: 0 22px 40px rgba(37, 99, 235, 0.14);

    .tool-icon {
      background: linear-gradient(135deg, #2563eb 0%, #0ea5e9 50%, #38bdf8 100%);
      color: #fff;
      box-shadow: 0 16px 28px rgba(37, 99, 235, 0.18);
    }
  }

  :deep(.el-card__body) {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 20px;
  }
}

.tool-icon {
  width: 56px;
  height: 56px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 16px;
  background: linear-gradient(135deg, #eff6ff 0%, #e0f2fe 100%);
  color: #2563eb;
  transition: all 0.25s ease;
}

.tool-info {
  h4 {
    margin-bottom: 6px;
    font-size: 16px;
    font-weight: 700;
    color: #0f172a;
  }

  p {
    margin: 0;
    color: #64748b;
    font-size: 14px;
    line-height: 1.6;
  }
}

@media (max-width: 768px) {
  .tool-cards {
    grid-template-columns: 1fr;
  }

  .tool-category h3 {
    width: 100%;
    justify-content: center;
  }
}
</style>
