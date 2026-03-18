<template>
  <div class="platform-converter">
    <el-card class="converter-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span class="title">
            <el-icon><Switch /></el-icon>
            多平台内容转换
          </span>
          <el-tooltip content="将已有内容一键转换为不同平台的格式">
            <el-icon class="help-icon"><QuestionFilled /></el-icon>
          </el-tooltip>
        </div>
      </template>

      <el-form :model="form" label-position="top">
        <!-- 原内容展示 -->
        <el-form-item label="原内容">
          <div v-if="originalContent" class="original-content">
            <div class="original-header">
              <el-tag type="info">{{ originalPlatformLabel }}</el-tag>
              <span class="original-title">{{ originalTitle }}</span>
            </div>
            <div class="original-preview">
              {{ originalContent.slice(0, 200) }}{{ originalContent.length > 200 ? '...' : '' }}
            </div>
          </div>
          <el-empty v-else description="请先选择要转换的内容" :image-size="60" />
        </el-form-item>

        <!-- 目标平台选择 -->
        <el-form-item label="目标平台">
          <div class="platform-grid">
            <div
              v-for="platform in platforms"
              :key="platform.code"
              class="platform-item"
              :class="{ 
                selected: selectedPlatforms.includes(platform.code),
                disabled: platform.code === originalPlatform
              }"
              @click="togglePlatform(platform.code)"
            >
              <span class="platform-icon">{{ PLATFORM_ICONS[platform.code as TargetPlatform] }}</span>
              <span class="platform-name">{{ platform.name }}</span>
              <el-icon v-if="selectedPlatforms.includes(platform.code)" class="check-icon">
                <Check />
              </el-icon>
            </div>
          </div>
        </el-form-item>

        <!-- 转换选项 -->
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item>
              <el-checkbox v-model="form.keep_structure">保留原文结构</el-checkbox>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item>
              <el-checkbox v-model="form.add_emojis">添加表情符号</el-checkbox>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item>
              <el-checkbox v-model="form.generate_tags">生成平台标签</el-checkbox>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="风格调整（可选）">
          <el-input
            v-model="form.style_adjustment"
            type="textarea"
            :rows="2"
            placeholder="例如：语气更轻松一些，添加一些互动引导"
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            :disabled="!originalContent || selectedPlatforms.length === 0"
            @click="handleConvert"
          >
            <el-icon><Refresh /></el-icon>
            {{ selectedPlatforms.length > 1 ? '批量转换' : '开始转换' }}
            <span v-if="selectedPlatforms.length > 0">({{ selectedPlatforms.length }}个平台)</span>
          </el-button>
        </el-form-item>
      </el-form>

      <!-- 转换结果 -->
      <div v-if="results.length > 0" class="convert-results">
        <el-divider>转换结果</el-divider>

        <el-tabs v-model="activeResultTab" type="border-card">
          <el-tab-pane
            v-for="(result, idx) in results"
            :key="idx"
            :label="PLATFORM_LABELS[result.target_platform as TargetPlatform] || result.target_platform"
            :name="String(idx)"
          >
            <div class="result-content">
              <div class="result-header">
                <h4 class="result-title">{{ result.converted_title }}</h4>
                <div class="result-stats">
                  <span><el-icon><Document /></el-icon> {{ result.word_count }} 字</span>
                </div>
              </div>

              <div class="result-body">
                <pre class="converted-text">{{ result.converted_content }}</pre>
              </div>

              <div v-if="result.tags.length > 0" class="result-tags">
                <span class="tags-label">推荐标签：</span>
                <el-tag
                  v-for="tag in result.tags"
                  :key="tag"
                  size="small"
                  type="info"
                  class="tag-item"
                >
                  #{{ tag }}
                </el-tag>
              </div>

              <div v-if="result.conversion_notes.length > 0" class="result-notes">
                <el-collapse>
                  <el-collapse-item title="转换说明">
                    <ul>
                      <li v-for="(note, i) in result.conversion_notes" :key="i">{{ note }}</li>
                    </ul>
                  </el-collapse-item>
                </el-collapse>
              </div>

              <div class="result-actions">
                <el-button type="primary" @click="copyResult(result)">
                  <el-icon><CopyDocument /></el-icon>
                  复制内容
                </el-button>
                <el-button @click="downloadResult(result)">
                  <el-icon><Download /></el-icon>
                  下载
                </el-button>
                <el-button v-if="result.creation_id" type="success" @click="viewCreation(result.creation_id)">
                  <el-icon><View /></el-icon>
                  查看记录
                </el-button>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, onMounted } from 'vue'
import {
  Switch,
  QuestionFilled,
  Refresh,
  Check,
  Document,
  CopyDocument,
  Download,
  View,
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import {
  getPlatforms,
  convertContent,
  batchConvert,
  TargetPlatform,
  PLATFORM_LABELS,
  PLATFORM_ICONS,
  type PlatformInfo,
  type ConvertResult,
} from '@/api/platformConverter'

// Props
const props = defineProps<{
  creationId?: number
  originalTitle?: string
  originalContent?: string
  originalPlatform?: string
}>()

// Emits
const emit = defineEmits<{
  (e: 'converted', results: ConvertResult[]): void
}>()

const router = useRouter()

// 状态
const loading = ref(false)
const platforms = ref<PlatformInfo[]>([])
const selectedPlatforms = ref<string[]>([])
const results = ref<ConvertResult[]>([])
const activeResultTab = ref('0')

// 表单
const form = reactive({
  keep_structure: true,
  add_emojis: false,
  generate_tags: true,
  style_adjustment: '',
})

// 计算属性
const originalPlatformLabel = computed(() => {
  if (!props.originalPlatform) return '未知平台'
  return PLATFORM_LABELS[props.originalPlatform as TargetPlatform] || props.originalPlatform
})

// 加载平台列表
const loadPlatforms = async () => {
  try {
    platforms.value = await getPlatforms()
  } catch (error) {
    console.error('加载平台列表失败:', error)
    // 使用默认平台列表
    platforms.value = Object.entries(PLATFORM_LABELS).map(([code, name]) => ({
      code,
      name,
      features: [],
      tips: [],
    }))
  }
}

// 切换平台选择
const togglePlatform = (code: string) => {
  if (code === props.originalPlatform) return
  
  const idx = selectedPlatforms.value.indexOf(code)
  if (idx > -1) {
    selectedPlatforms.value.splice(idx, 1)
  } else {
    if (selectedPlatforms.value.length >= 5) {
      ElMessage.warning('最多同时选择5个平台')
      return
    }
    selectedPlatforms.value.push(code)
  }
}

// 执行转换
const handleConvert = async () => {
  if (!props.creationId) {
    ElMessage.warning('请先选择要转换的内容')
    return
  }
  
  if (selectedPlatforms.value.length === 0) {
    ElMessage.warning('请选择目标平台')
    return
  }

  loading.value = true
  results.value = []

  try {
    if (selectedPlatforms.value.length === 1) {
      // 单个平台转换
      const result = await convertContent({
        creation_id: props.creationId,
        target_platform: selectedPlatforms.value[0] as TargetPlatform,
        keep_structure: form.keep_structure,
        add_emojis: form.add_emojis,
        generate_tags: form.generate_tags,
        style_adjustment: form.style_adjustment || undefined,
      })
      results.value = [result]
    } else {
      // 批量转换
      const batchResult = await batchConvert({
        creation_id: props.creationId,
        target_platforms: selectedPlatforms.value as TargetPlatform[],
        style_adjustment: form.style_adjustment || undefined,
      })
      results.value = batchResult.results
      
      if (batchResult.failed_count > 0) {
        ElMessage.warning(`${batchResult.success_count}个平台转换成功，${batchResult.failed_count}个失败`)
      }
    }

    if (results.value.length > 0) {
      ElMessage.success('转换完成')
      emit('converted', results.value)
    }
  } catch (error: any) {
    ElMessage.error(error.message || '转换失败，请重试')
  } finally {
    loading.value = false
  }
}

// 复制结果
const copyResult = async (result: ConvertResult) => {
  const text = `${result.converted_title}\n\n${result.converted_content}`
  try {
    await navigator.clipboard.writeText(text)
    ElMessage.success('已复制到剪贴板')
  } catch {
    ElMessage.error('复制失败')
  }
}

// 下载结果
const downloadResult = (result: ConvertResult) => {
  const text = `${result.converted_title}\n\n${result.converted_content}`
  const blob = new Blob([text], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${result.converted_title.slice(0, 20)}_${result.target_platform}.txt`
  a.click()
  URL.revokeObjectURL(url)
}

// 查看创作记录
const viewCreation = (creationId: number) => {
  router.push(`/creations/${creationId}`)
}

// 监听内容变化
watch(() => props.creationId, () => {
  results.value = []
  selectedPlatforms.value = []
})

onMounted(() => {
  loadPlatforms()
})

// 暴露方法
defineExpose({
  reset: () => {
    results.value = []
    selectedPlatforms.value = []
    form.style_adjustment = ''
  },
})
</script>

<style scoped lang="scss">
.platform-converter {
  .converter-card {
    border-radius: 12px;
  }

  .card-header {
    display: flex;
    align-items: center;
    gap: 8px;

    .title {
      display: flex;
      align-items: center;
      gap: 6px;
      font-weight: 600;
      font-size: 16px;
    }

    .help-icon {
      color: #909399;
      cursor: help;
    }
  }

  .original-content {
    width: 100%;
    padding: 16px;
    background: #f5f7fa;
    border-radius: 8px;

    .original-header {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 12px;

      .original-title {
        font-weight: 600;
        color: #303133;
      }
    }

    .original-preview {
      font-size: 14px;
      color: #606266;
      line-height: 1.6;
    }
  }

  .platform-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
    gap: 12px;
    width: 100%;

    .platform-item {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 8px;
      padding: 16px 12px;
      border: 2px solid #e4e7ed;
      border-radius: 12px;
      cursor: pointer;
      transition: all 0.2s;
      position: relative;

      &:hover:not(.disabled) {
        border-color: #409eff;
        background: rgba(64, 158, 255, 0.05);
      }

      &.selected {
        border-color: #409eff;
        background: rgba(64, 158, 255, 0.1);
      }

      &.disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }

      .platform-icon {
        font-size: 24px;
      }

      .platform-name {
        font-size: 13px;
        color: #606266;
      }

      .check-icon {
        position: absolute;
        top: 8px;
        right: 8px;
        color: #409eff;
        font-size: 16px;
      }
    }
  }

  .convert-results {
    margin-top: 20px;

    .result-content {
      padding: 16px;

      .result-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 16px;

        .result-title {
          margin: 0;
          font-size: 18px;
          font-weight: 600;
          color: #303133;
        }

        .result-stats {
          display: flex;
          gap: 16px;
          font-size: 13px;
          color: #909399;

          span {
            display: flex;
            align-items: center;
            gap: 4px;
          }
        }
      }

      .result-body {
        margin-bottom: 16px;

        .converted-text {
          margin: 0;
          padding: 16px;
          background: #f5f7fa;
          border-radius: 8px;
          font-size: 14px;
          line-height: 1.8;
          white-space: pre-wrap;
          word-break: break-word;
          font-family: inherit;
          max-height: 400px;
          overflow-y: auto;
        }
      }

      .result-tags {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 8px;
        margin-bottom: 16px;

        .tags-label {
          font-size: 13px;
          color: #909399;
        }

        .tag-item {
          cursor: pointer;

          &:hover {
            opacity: 0.8;
          }
        }
      }

      .result-notes {
        margin-bottom: 16px;

        ul {
          margin: 0;
          padding-left: 20px;

          li {
            font-size: 13px;
            color: #606266;
            line-height: 1.8;
          }
        }
      }

      .result-actions {
        display: flex;
        gap: 12px;
        padding-top: 16px;
        border-top: 1px solid #ebeef5;
      }
    }
  }
}
</style>
