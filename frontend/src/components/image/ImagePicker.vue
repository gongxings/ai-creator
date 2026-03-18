<template>
  <div class="image-picker">
    <el-dialog
      v-model="visible"
      title="选择配图"
      width="900px"
      :close-on-click-modal="false"
      destroy-on-close
    >
      <div class="picker-content">
        <!-- 搜索区 -->
        <div class="search-section">
          <el-input
            v-model="searchQuery"
            placeholder="输入关键词搜索图片..."
            class="search-input"
            @keyup.enter="handleSearch"
          >
            <template #append>
              <el-button :loading="loading" @click="handleSearch">
                <el-icon><Search /></el-icon>
                搜索
              </el-button>
            </template>
          </el-input>

          <div class="search-filters">
            <el-select v-model="filters.source" placeholder="图库来源" clearable>
              <el-option label="全部图库" :value="undefined" />
              <el-option label="Unsplash" value="unsplash" />
              <el-option label="Pexels" value="pexels" />
            </el-select>
            <el-select v-model="filters.orientation" placeholder="图片方向" clearable>
              <el-option label="全部方向" :value="undefined" />
              <el-option label="横向" value="landscape" />
              <el-option label="纵向" value="portrait" />
              <el-option label="正方形" value="square" />
            </el-select>
            <el-button
              v-if="contentForSuggest"
              type="primary"
              text
              :loading="suggestLoading"
              @click="handleSuggestKeywords"
            >
              <el-icon><MagicStick /></el-icon>
              AI推荐关键词
            </el-button>
          </div>

          <!-- AI推荐关键词 -->
          <div v-if="suggestedKeywords.length > 0" class="suggested-keywords">
            <span class="label">推荐关键词：</span>
            <el-tag
              v-for="keyword in suggestedKeywords"
              :key="keyword"
              class="keyword-tag"
              @click="searchQuery = keyword; handleSearch()"
            >
              {{ keyword }}
            </el-tag>
          </div>
        </div>

        <!-- 图片网格 -->
        <div v-if="loading" class="loading-state">
          <el-skeleton :rows="3" animated />
        </div>

        <div v-else-if="images.length === 0" class="empty-state">
          <el-empty :description="hasSearched ? '没有找到相关图片' : '请输入关键词搜索图片'" />
        </div>

        <div v-else class="image-grid">
          <div
            v-for="image in images"
            :key="image.id"
            class="image-item"
            :class="{ selected: selectedImage?.id === image.id }"
            @click="selectImage(image)"
          >
            <div class="image-wrapper">
              <img :src="image.thumb_url" :alt="image.alt" loading="lazy" />
              <div class="image-overlay">
                <el-icon class="check-icon"><Check /></el-icon>
              </div>
            </div>
            <div class="image-info">
              <span class="source-badge" :class="image.source">
                {{ SOURCE_LABELS[image.source] }}
              </span>
              <span v-if="image.photographer" class="photographer">
                {{ image.photographer }}
              </span>
            </div>
          </div>
        </div>

        <!-- 分页 -->
        <div v-if="total > perPage" class="pagination">
          <el-pagination
            v-model:current-page="currentPage"
            :page-size="perPage"
            :total="total"
            layout="prev, pager, next"
            @current-change="handlePageChange"
          />
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <div v-if="selectedImage" class="selected-preview">
            <img :src="selectedImage.thumb_url" :alt="selectedImage.alt" />
            <span>已选择</span>
          </div>
          <div class="footer-actions">
            <el-button @click="visible = false">取消</el-button>
            <el-button type="primary" :disabled="!selectedImage" @click="handleConfirm">
              确认选择
            </el-button>
          </div>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { Search, MagicStick, Check } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import {
  searchImages,
  suggestKeywords,
  SOURCE_LABELS,
  ImageSource,
  ImageOrientation,
  type ImageItem,
} from '@/api/imageStock'

// Props
const props = defineProps<{
  contentForSuggest?: string  // 用于 AI 推荐关键词的内容
}>()

// Emits
const emit = defineEmits<{
  (e: 'select', image: ImageItem): void
}>()

// 状态
const visible = ref(false)
const loading = ref(false)
const suggestLoading = ref(false)
const hasSearched = ref(false)
const searchQuery = ref('')
const images = ref<ImageItem[]>([])
const selectedImage = ref<ImageItem | null>(null)
const total = ref(0)
const currentPage = ref(1)
const perPage = 20
const suggestedKeywords = ref<string[]>([])

// 筛选条件
const filters = reactive({
  source: undefined as ImageSource | undefined,
  orientation: undefined as ImageOrientation | undefined,
})

// 搜索图片
const handleSearch = async () => {
  if (!searchQuery.value.trim()) {
    ElMessage.warning('请输入搜索关键词')
    return
  }

  loading.value = true
  hasSearched.value = true
  currentPage.value = 1

  try {
    const result = await searchImages({
      query: searchQuery.value,
      source: filters.source,
      orientation: filters.orientation,
      page: currentPage.value,
      per_page: perPage,
    })
    images.value = result.images
    total.value = result.total
  } catch (error: any) {
    ElMessage.error(error.message || '搜索失败')
    images.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

// 翻页
const handlePageChange = async (page: number) => {
  loading.value = true

  try {
    const result = await searchImages({
      query: searchQuery.value,
      source: filters.source,
      orientation: filters.orientation,
      page,
      per_page: perPage,
    })
    images.value = result.images
    total.value = result.total
  } catch (error: any) {
    ElMessage.error(error.message || '加载失败')
  } finally {
    loading.value = false
  }
}

// AI 推荐关键词
const handleSuggestKeywords = async () => {
  if (!props.contentForSuggest) return

  suggestLoading.value = true

  try {
    const result = await suggestKeywords({
      content: props.contentForSuggest,
      count: 5,
    })
    // 合并中英文关键词
    suggestedKeywords.value = [...result.keywords, ...result.keywords_en].slice(0, 8)
  } catch (error: any) {
    ElMessage.error(error.message || '获取推荐关键词失败')
  } finally {
    suggestLoading.value = false
  }
}

// 选择图片
const selectImage = (image: ImageItem) => {
  selectedImage.value = image
}

// 确认选择
const handleConfirm = () => {
  if (selectedImage.value) {
    emit('select', selectedImage.value)
    visible.value = false
  }
}

// 打开选择器
const open = (defaultQuery?: string) => {
  visible.value = true
  selectedImage.value = null
  if (defaultQuery) {
    searchQuery.value = defaultQuery
    handleSearch()
  }
}

// 监听筛选条件变化，自动重新搜索
watch(filters, () => {
  if (hasSearched.value) {
    handleSearch()
  }
}, { deep: true })

// 暴露方法
defineExpose({
  open,
})
</script>

<style scoped lang="scss">
.picker-content {
  .search-section {
    margin-bottom: 20px;

    .search-input {
      margin-bottom: 12px;
    }

    .search-filters {
      display: flex;
      gap: 12px;
      align-items: center;
      flex-wrap: wrap;

      .el-select {
        width: 140px;
      }
    }

    .suggested-keywords {
      display: flex;
      align-items: center;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 12px;
      padding: 12px;
      background: #f5f7fa;
      border-radius: 8px;

      .label {
        font-size: 13px;
        color: #606266;
      }

      .keyword-tag {
        cursor: pointer;
        transition: all 0.2s;

        &:hover {
          transform: scale(1.05);
        }
      }
    }
  }

  .loading-state,
  .empty-state {
    padding: 40px 0;
  }

  .image-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: 16px;
    max-height: 400px;
    overflow-y: auto;
    padding: 4px;

    .image-item {
      position: relative;
      cursor: pointer;
      border-radius: 12px;
      overflow: hidden;
      transition: all 0.2s;
      background: #f5f7fa;

      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.12);
      }

      &.selected {
        .image-overlay {
          opacity: 1;
        }
      }

      .image-wrapper {
        position: relative;
        aspect-ratio: 4/3;
        overflow: hidden;

        img {
          width: 100%;
          height: 100%;
          object-fit: cover;
          transition: transform 0.3s;
        }

        &:hover img {
          transform: scale(1.05);
        }

        .image-overlay {
          position: absolute;
          inset: 0;
          background: rgba(64, 158, 255, 0.6);
          display: flex;
          align-items: center;
          justify-content: center;
          opacity: 0;
          transition: opacity 0.2s;

          .check-icon {
            font-size: 40px;
            color: white;
          }
        }
      }

      .image-info {
        padding: 8px 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 12px;

        .source-badge {
          padding: 2px 8px;
          border-radius: 4px;
          font-weight: 500;

          &.unsplash {
            background: #111;
            color: white;
          }

          &.pexels {
            background: #05a081;
            color: white;
          }
        }

        .photographer {
          color: #909399;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
          max-width: 100px;
        }
      }
    }
  }

  .pagination {
    display: flex;
    justify-content: center;
    margin-top: 20px;
  }
}

.dialog-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;

  .selected-preview {
    display: flex;
    align-items: center;
    gap: 10px;

    img {
      width: 50px;
      height: 50px;
      object-fit: cover;
      border-radius: 8px;
    }

    span {
      color: #67c23a;
      font-size: 14px;
      font-weight: 500;
    }
  }

  .footer-actions {
    display: flex;
    gap: 10px;
  }
}
</style>
