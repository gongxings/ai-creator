<template>
  <div class="hotspot-panel">
    <div class="panel-header">
      <div class="title-row">
        <h3>
          <el-icon><TrendCharts /></el-icon>
          今日热点
        </h3>
        <div class="actions">
          <el-button text size="small" @click="refreshCurrentPlatform" :loading="loading">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
          <el-button
            v-if="!collapsed"
            text
            size="small"
            @click="collapsed = true"
          >
            <el-icon><ArrowUp /></el-icon>
            收起
          </el-button>
          <el-button v-else text size="small" @click="collapsed = false">
            <el-icon><ArrowDown /></el-icon>
            展开
          </el-button>
        </div>
      </div>

      <!-- 分类标签栏 -->
      <div class="category-tabs">
        <div class="tabs-scroll">
          <el-tag
            v-for="cat in categories"
            :key="cat.code"
            :effect="activeCategory === cat.code ? 'dark' : 'plain'"
            :type="activeCategory === cat.code ? 'primary' : 'info'"
            class="category-tag"
            @click="selectCategory(cat.code)"
          >
            {{ cat.name }}
          </el-tag>
        </div>
      </div>

      <!-- 平台标签栏 -->
      <div class="platform-tabs">
        <div class="tabs-scroll">
          <el-tag
            v-for="platform in filteredPlatforms"
            :key="platform.code"
            :effect="activePlatform === platform.code ? 'dark' : 'plain'"
            :style="getPlatformTagStyle(platform)"
            class="platform-tag"
            @click="selectPlatform(platform)"
          >
            {{ platform.name }}
          </el-tag>
        </div>
      </div>
    </div>

    <div v-show="!collapsed" class="panel-content">
      <div v-if="loading" class="loading-state">
        <el-skeleton :rows="5" animated />
      </div>

      <div v-else-if="hotItems.length === 0" class="empty-state">
        <el-empty description="暂无热点数据" :image-size="60" />
      </div>

      <div v-else class="hot-list">
        <div
          v-for="(item, index) in hotItems.slice(0, displayCount)"
          :key="index"
          class="hot-item"
          @click="openHotLink(item)"
        >
          <span class="rank" :class="getRankClass(index)">{{ index + 1 }}</span>
          <span class="title">{{ item.title }}</span>
          <span v-if="item.hot" class="hot-value">{{ formatHot(item.hot) }}</span>
          <div class="item-actions">
            <el-dropdown trigger="click" @command="(cmd: string) => handleWriteCommand(cmd, item)">
              <el-button type="primary" size="small" link @click.stop>
                <el-icon><Edit /></el-icon>
                写作
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="wechat_article">
                    <el-icon><Document /></el-icon>
                    写公众号文章
                  </el-dropdown-item>
                  <el-dropdown-item command="xiaohongshu_note">
                    <el-icon><ChatDotRound /></el-icon>
                    写小红书笔记
                  </el-dropdown-item>
                  <el-dropdown-item command="video_script">
                    <el-icon><VideoCamera /></el-icon>
                    写短视频脚本
                  </el-dropdown-item>
                  <el-dropdown-item divided command="ai_suggest">
                    <el-icon><MagicStick /></el-icon>
                    AI 选题建议
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>

        <div v-if="hotItems.length > displayCount" class="show-more">
          <el-button text type="primary" @click="displayCount += 10">
            显示更多 ({{ hotItems.length - displayCount }} 条)
          </el-button>
        </div>
      </div>
    </div>

    <!-- AI 选题建议弹窗 -->
    <TopicSuggestDialog
      v-model:visible="suggestDialogVisible"
      :hot-title="selectedHotTitle"
      :hot-url="selectedHotUrl"
      @select="onSelectAngle"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  TrendCharts,
  Refresh,
  ArrowUp,
  ArrowDown,
  Edit,
  Document,
  ChatDotRound,
  VideoCamera,
  MagicStick,
} from '@element-plus/icons-vue'
import { ElMessage, ElLoading } from 'element-plus'
import { getHotList, getPlatforms, getCategories, extractKeywords } from '@/api/hotspot'
import type { HotspotItem, PlatformInfo, CategoryInfo } from '@/api/hotspot'
import TopicSuggestDialog from './TopicSuggestDialog.vue'
import { useHotspotWritingStore } from '@/store/hotspotWriting'

const router = useRouter()

// 状态
const loading = ref(false)
const collapsed = ref(false)
const displayCount = ref(10)

// 分类相关
const categories = ref<CategoryInfo[]>([])
const activeCategory = ref('all')

// 平台相关
const platforms = ref<PlatformInfo[]>([])
const activePlatform = ref('weibo')

// 热点数据
const hotItems = ref<HotspotItem[]>([])

// AI 选题建议弹窗
const suggestDialogVisible = ref(false)
const selectedHotTitle = ref('')
const selectedHotUrl = ref('')

// 根据分类筛选平台
const filteredPlatforms = computed(() => {
  if (activeCategory.value === 'all') {
    return platforms.value
  }
  return platforms.value.filter(p => p.category === activeCategory.value)
})

// 加载分类列表
const loadCategories = async () => {
  try {
    const res = await getCategories()
    categories.value = res.categories
  } catch (error) {
    console.error('加载分类列表失败:', error)
    // 使用默认分类
    categories.value = [
      { code: 'all', name: '全部', order: 0 },
      { code: 'social', name: '社交媒体', order: 1 },
      { code: 'news', name: '新闻资讯', order: 2 },
      { code: 'tech', name: '科技数码', order: 3 },
      { code: 'dev', name: '开发者', order: 4 },
      { code: 'knowledge', name: '知识社区', order: 5 },
      { code: 'game', name: '游戏动漫', order: 6 },
      { code: 'entertainment', name: '影音娱乐', order: 7 },
      { code: 'international', name: '国际媒体', order: 8 },
      { code: 'other', name: '其他', order: 9 },
    ]
  }
}

// 加载平台列表
const loadPlatforms = async () => {
  try {
    const res = await getPlatforms()
    platforms.value = res.platforms
    // 确保当前平台存在
    if (platforms.value.length > 0 && !platforms.value.find(p => p.code === activePlatform.value)) {
      activePlatform.value = platforms.value[0].code
    }
  } catch (error) {
    console.error('加载平台列表失败:', error)
    // 使用默认平台列表（不包含百度）
    platforms.value = [
      { code: 'weibo', name: '微博', category: 'social', color: '#E6162D' },
      { code: 'zhihu', name: '知乎', category: 'knowledge', color: '#0084FF' },
      { code: 'douyin', name: '抖音', category: 'social', color: '#000000' },
      { code: 'bilibili', name: 'B站', category: 'social', color: '#FB7299' },
      { code: 'toutiao', name: '头条', category: 'news', color: '#F85959' },
    ]
  }
}

// 加载热点列表
const loadHotList = async (platform: string) => {
  loading.value = true
  displayCount.value = 10
  try {
    const res = await getHotList(platform, 50)
    hotItems.value = res.items
  } catch (error) {
    console.error('加载热点列表失败:', error)
    hotItems.value = []
    ElMessage.error('加载热点失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 选择分类
const selectCategory = (code: string) => {
  activeCategory.value = code
  // 如果当前平台不在新分类中，切换到该分类的第一个平台
  const platformsInCategory = code === 'all' 
    ? platforms.value 
    : platforms.value.filter(p => p.category === code)
  
  if (platformsInCategory.length > 0 && !platformsInCategory.find(p => p.code === activePlatform.value)) {
    selectPlatform(platformsInCategory[0])
  }
}

// 选择平台
const selectPlatform = (platform: PlatformInfo) => {
  activePlatform.value = platform.code
  loadHotList(platform.code)
}

// 刷新当前平台
const refreshCurrentPlatform = () => {
  loadHotList(activePlatform.value)
}

// 获取平台标签样式
const getPlatformTagStyle = (platform: PlatformInfo) => {
  if (activePlatform.value === platform.code && platform.color) {
    return {
      backgroundColor: platform.color,
      borderColor: platform.color,
      color: '#fff',
    }
  }
  return {}
}

// 打开热点链接
const openHotLink = (item: HotspotItem) => {
  if (item.url) {
    window.open(item.url, '_blank')
  }
}

// 处理写作命令
const handleWriteCommand = async (command: string, item: HotspotItem) => {
  const hotspotStore = useHotspotWritingStore()
  
  if (command === 'ai_suggest') {
    selectedHotTitle.value = item.title
    selectedHotUrl.value = item.url || ''
    suggestDialogVisible.value = true
  } else {
    // 先提取关键词（包括获取URL内容），再跳转到写作编辑器
    const loadingInstance = ElLoading.service({
      text: '正在分析热点内容...',
      background: 'rgba(255, 255, 255, 0.8)',
    })
    
    try {
      // 传递 URL 给后端
      const res = await extractKeywords(item.title, item.url)
      const keywords = res.keywords?.join(',') || ''
      const additionalDescription = res.additional_description || ''
      
      console.log('提取关键词结果:', { keywords, additionalDescription })
      
      // 存储到 Pinia
      hotspotStore.setHotspotData({
        topic: item.title,
        keywords: keywords,
        additional_description: additionalDescription,
        tool_type: command,
      })
      
    } catch (error) {
      console.error('提取关键词失败:', error)
      // 提取失败也跳转，只是没有关键词
      hotspotStore.setHotspotData({
        topic: item.title,
        keywords: '',
        additional_description: '',
        tool_type: command,
      })
    } finally {
      loadingInstance.close()
    }
    
    // 跳转到写作编辑器，只需传递工具类型
    router.push({
      name: 'WritingEditor',
      params: { toolType: command },
    })
  }
}

// 选择 AI 建议的角度
const onSelectAngle = (data: { toolType: string; title: string; direction: string; keywords?: string[]; additionalDescription?: string }) => {
  const hotspotStore = useHotspotWritingStore()
  
  // 存储到 Pinia
  hotspotStore.setHotspotData({
    topic: data.title,
    keywords: data.keywords?.join(',') || '',
    additional_description: data.additionalDescription || '',
    tool_type: data.toolType,
  })
  
  // 跳转只需传递工具类型
  router.push({
    name: 'WritingEditor',
    params: { toolType: data.toolType },
  })
}

// 排名样式
const getRankClass = (index: number) => {
  if (index === 0) return 'top-1'
  if (index === 1) return 'top-2'
  if (index === 2) return 'top-3'
  return ''
}

// 格式化热度
const formatHot = (hot: number) => {
  if (hot >= 10000) {
    return (hot / 10000).toFixed(1) + '万'
  }
  return hot.toString()
}

// 初始化
onMounted(async () => {
  await Promise.all([loadCategories(), loadPlatforms()])
  loadHotList(activePlatform.value)
})
</script>

<style scoped lang="scss">
.hotspot-panel {
  background: rgba(255, 255, 255, 0.9);
  border-radius: 16px;
  border: 1px solid rgba(148, 163, 184, 0.15);
  overflow: hidden;
  margin-bottom: 24px;
}

.panel-header {
  padding: 16px 20px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.1);

  .title-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 12px;

    h3 {
      display: flex;
      align-items: center;
      gap: 8px;
      margin: 0;
      font-size: 16px;
      font-weight: 600;
      color: #1e293b;

      .el-icon {
        color: #f97316;
      }
    }

    .actions {
      display: flex;
      gap: 4px;
    }
  }
}

// 分类标签栏
.category-tabs {
  margin-bottom: 12px;

  .tabs-scroll {
    display: flex;
    gap: 8px;
    overflow-x: auto;
    padding: 4px 0;
    scrollbar-width: thin;

    &::-webkit-scrollbar {
      height: 4px;
    }

    &::-webkit-scrollbar-thumb {
      background: rgba(148, 163, 184, 0.3);
      border-radius: 2px;
    }
  }

  .category-tag {
    cursor: pointer;
    flex-shrink: 0;
    font-size: 13px;
    padding: 6px 14px;
    border-radius: 16px;
    transition: all 0.2s;

    &:hover {
      opacity: 0.85;
    }
  }
}

// 平台标签栏
.platform-tabs {
  .tabs-scroll {
    display: flex;
    gap: 8px;
    overflow-x: auto;
    padding: 4px 0;
    scrollbar-width: thin;

    &::-webkit-scrollbar {
      height: 4px;
    }

    &::-webkit-scrollbar-thumb {
      background: rgba(148, 163, 184, 0.3);
      border-radius: 2px;
    }
  }

  .platform-tag {
    cursor: pointer;
    flex-shrink: 0;
    font-size: 13px;
    padding: 6px 12px;
    border-radius: 16px;
    transition: all 0.2s;

    &:hover {
      opacity: 0.85;
    }
  }
}

.panel-content {
  padding: 12px 16px;
  max-height: 400px;
  overflow-y: auto;
}

.loading-state,
.empty-state {
  padding: 20px 0;
}

.hot-list {
  .hot-item {
    display: flex;
    align-items: center;
    padding: 10px 12px;
    border-radius: 8px;
    cursor: pointer;
    transition: background-color 0.2s;

    &:hover {
      background: rgba(59, 130, 246, 0.05);

      .item-actions {
        opacity: 1;
      }
    }

    .rank {
      flex-shrink: 0;
      width: 24px;
      height: 24px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 12px;
      font-weight: 600;
      border-radius: 6px;
      background: #f1f5f9;
      color: #64748b;
      margin-right: 12px;

      &.top-1 {
        background: linear-gradient(135deg, #f97316, #ea580c);
        color: white;
      }

      &.top-2 {
        background: linear-gradient(135deg, #fb923c, #f97316);
        color: white;
      }

      &.top-3 {
        background: linear-gradient(135deg, #fdba74, #fb923c);
        color: white;
      }
    }

    .title {
      flex: 1;
      font-size: 14px;
      color: #334155;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .hot-value {
      flex-shrink: 0;
      font-size: 12px;
      color: #94a3b8;
      margin-left: 12px;
      margin-right: 8px;
    }

    .item-actions {
      flex-shrink: 0;
      opacity: 0;
      transition: opacity 0.2s;
    }
  }

  .show-more {
    text-align: center;
    padding: 12px 0;
  }
}
</style>
