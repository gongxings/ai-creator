<template>
  <div class="video-generation flagship-page page-shell">
    <section class="page-hero video-hero">
      <div class="hero-grid">
        <div class="hero-content">
          <h1>AI视频生成</h1>
          <p class="hero-subtitle">使用AI技术，将文字或图片转换为精彩视频</p>
        </div>
        <div class="hero-panel">
          <div class="hero-panel-row">
            <!-- 视频策略 -->
            <div class="hero-panel-section">
              <div class="section-title">视频策略</div>
              <div class="info-list compact">
                <div class="info-item">
                  <div class="info-icon">
                    <el-icon><VideoCamera /></el-icon>
                  </div>
                  <div class="info-text">
                    <div class="info-title">明确主体</div>
                    <div class="info-desc">描述主角、动作与环境</div>
                  </div>
                </div>
                <div class="info-item">
                  <div class="info-icon">
                    <el-icon><UploadFilled /></el-icon>
                  </div>
                  <div class="info-text">
                    <div class="info-title">补充运镜</div>
                    <div class="info-desc">加入推进、环绕或慢镜头效果</div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 参数摘要 -->
            <div class="hero-panel-section">
              <div class="section-title">参数摘要</div>
              <div class="info-list compact">
                <div class="info-item">
                  <div class="info-text">
                    <div class="info-title">AI模式</div>
                    <div class="info-desc">
                      {{ aiMode }}（{{
                        aiMode === "Cookie" ? selectedPlatform : "消耗积分"
                      }}）
                    </div>
                  </div>
                </div>
                <div class="info-item">
                  <div class="info-text">
                    <div class="info-title">视频时长</div>
                    <div class="info-desc">
                      {{
                        activeTab === "text"
                          ? textForm.duration
                          : imageForm.duration
                      }}秒
                    </div>
                  </div>
                </div>
                <div class="info-item">
                  <div class="info-text">
                    <div class="info-title">画面比例</div>
                    <div class="info-desc">
                      {{
                        activeTab === "text"
                          ? textForm.aspect_ratio
                          : "图片转视频"
                      }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 以下部分保持原结构不变 -->
    <section class="page-dashboard">
      <div class="dashboard-grid">
        <div class="dashboard-card">
          <div class="label">当前模式</div>
          <div class="value">
            {{ activeTab === "text" ? "文本生成" : "图片生成" }}
          </div>
          <div class="delta">支持多种风格与比例</div>
        </div>
        <div class="dashboard-card">
          <div class="label">历史任务</div>
          <div class="value">{{ historyList.length }}</div>
          <div class="delta">随时回看生成结果</div>
        </div>
        <div class="dashboard-card">
          <div class="label">任务状态</div>
          <div class="value">
            {{
              currentTask
                ? currentTask.status === "processing"
                  ? "生成中"
                  : currentTask.status === "completed"
                  ? "已完成"
                  : "失败"
                : "空闲"
            }}
          </div>
          <div class="delta">平均等待约 1-3 分钟</div>
        </div>
      </div>
    </section>

    <section class="page-body">
      <div class="main-panel">
        <el-row :gutter="[1, 1]">
          <!-- 左侧：输入区域 -->
          <el-col :xs="24" :sm="24" :md="24" :lg="12">
            <el-card class="input-card">
              <template #header>
                <div class="card-header">
                  <span>视频生成</span>
                  <el-button
                    type="primary"
                    :loading="generating"
                    @click="generateVideo"
                  >
                    <el-icon><VideoCamera /></el-icon>
                    生成视频
                  </el-button>
                </div>
              </template>

              <el-tabs v-model="activeTab" class="custom-tabs">
                <!-- 文本生成视频 -->
                <el-tab-pane label="文本生成视频" name="text">
                  <el-form :model="textForm" label-position="top">
                    <el-form-item label="视频描述" required>
                      <el-input
                        v-model="textForm.prompt"
                        type="textarea"
                        :rows="6"
                        placeholder="请详细描述你想要生成的视频内容，例如：一只可爱的小猫在花园里追逐蝴蝶，阳光明媚，画面温馨"
                        maxlength="2000"
                        show-word-limit
                      />
                    </el-form-item>

                    <el-row :gutter="[12, 12]">
                      <el-col :xs="24" :sm="12">
                        <el-form-item label="视频时长">
                          <el-select
                            v-model="textForm.duration"
                            placeholder="请选择时长"
                            style="width: 100%"
                          >
                            <el-option label="5秒" :value="5" />
                            <el-option label="10秒" :value="10" />
                            <el-option label="15秒" :value="15" />
                            <el-option label="30秒" :value="30" />
                          </el-select>
                        </el-form-item>
                      </el-col>
                      <el-col :xs="24" :sm="12">
                        <el-form-item label="视频风格">
                          <el-select
                            v-model="textForm.style"
                            placeholder="请选择风格"
                            style="width: 100%"
                          >
                            <el-option label="真实" value="realistic" />
                            <el-option label="动画" value="animated" />
                            <el-option label="艺术" value="artistic" />
                          </el-select>
                        </el-form-item>
                      </el-col>
                    </el-row>

                    <el-form-item label="视频比例">
                      <el-radio-group
                        v-model="textForm.aspect_ratio"
                        class="ratio-group"
                      >
                        <el-radio-button label="16:9">
                          <div class="ratio-option">
                            <div class="ratio-icon landscape"></div>
                            <span>横屏 16:9</span>
                          </div>
                        </el-radio-button>
                        <el-radio-button label="9:16">
                          <div class="ratio-option">
                            <div class="ratio-icon portrait"></div>
                            <span>竖屏 9:16</span>
                          </div>
                        </el-radio-button>
                        <el-radio-button label="1:1">
                          <div class="ratio-option">
                            <div class="ratio-icon square"></div>
                            <span>方形 1:1</span>
                          </div>
                        </el-radio-button>
                      </el-radio-group>
                    </el-form-item>
                  </el-form>
                </el-tab-pane>

                <!-- 图片生成视频 -->
                <el-tab-pane label="图片生成视频" name="image">
                  <el-form :model="imageForm" label-position="top">
                    <el-form-item label="上传图片" required>
                      <el-upload
                        class="upload-area"
                        drag
                        :auto-upload="false"
                        :on-change="handleImageChange"
                        :limit="1"
                        accept="image/*"
                      >
                        <el-icon class="el-icon--upload"
                          ><upload-filled
                        /></el-icon>
                        <div class="el-upload__text">
                          拖拽图片到此处或<em>点击上传</em>
                        </div>
                        <template #tip>
                          <div class="el-upload__tip">
                            支持 jpg/png 格式，建议尺寸 1920x1080
                          </div>
                        </template>
                      </el-upload>
                    </el-form-item>

                    <el-form-item label="运动描述">
                      <el-input
                        v-model="imageForm.motion_prompt"
                        type="textarea"
                        :rows="3"
                        placeholder="描述图片中的运动效果，例如：镜头缓慢推进，人物微笑"
                        maxlength="500"
                        show-word-limit
                      />
                    </el-form-item>

                    <el-form-item label="视频时长">
                      <el-select
                        v-model="imageForm.duration"
                        placeholder="请选择时长"
                        style="width: 100%"
                      >
                        <el-option label="5秒" :value="5" />
                        <el-option label="10秒" :value="10" />
                      </el-select>
                    </el-form-item>
                  </el-form>
                </el-tab-pane>
              </el-tabs>

              <!-- AI服务选择卡片 -->
              <el-card shadow="never" class="model-card">
                <template #header><span>AI服务</span></template>

                <el-form-item label="使用模式">
                  <el-segmented
                    v-model="aiMode"
                    :options="['API Key', 'Cookie']"
                    block
                  />
                </el-form-item>

                <template v-if="aiMode === 'API Key'">
                  <el-alert type="info" title="API Key模式" :closable="false">
                    <p>使用配置的API Key调用，需消耗积分</p>
                  </el-alert>
                </template>

                <template v-else>
                  <el-form-item label="选择平台">
                    <el-select
                      v-model="selectedPlatform"
                      placeholder="选择AI平台"
                      style="width: 100%"
                    >
                      <el-option label="豆包 (Doubao)" value="doubao" />
                      <el-option label="通义千问 (Qwen)" value="qwen" />
                      <el-option label="Runway" value="runway" />
                    </el-select>
                  </el-form-item>
                  <el-alert type="success" title="Cookie模式" :closable="false">
                    <p>使用已授权账号的免费额度</p>
                  </el-alert>
                </template>
              </el-card>
            </el-card>
          </el-col>

          <!-- 右侧：预览区域 -->
          <el-col :xs="24" :sm="24" :md="24" :lg="12">
            <el-card class="preview-card">
              <template #header>
                <div class="card-header">
                  <span>视频预览</span>
                  <el-tag
                    v-if="currentTask && currentTask.status === 'processing'"
                    type="warning"
                  >
                    生成中 {{ currentTask.progress }}%
                  </el-tag>
                  <el-tag
                    v-else-if="currentTask && currentTask.status === 'completed'"
                    type="success"
                  >
                    已完成
                  </el-tag>
                </div>
              </template>

              <div v-if="currentTask" class="result-content">
                <div
                  v-if="currentTask.status === 'processing'"
                  class="generating-state"
                >
                  <div class="progress-circle">
                    <el-progress
                      type="circle"
                      :percentage="currentTask.progress"
                      :width="100"
                    />
                  </div>
                  <p class="progress-text">视频生成中...</p>
                  <p class="progress-hint">预计还需 {{ currentTask.estimated_time }} 秒</p>
                </div>

                <el-alert
                  v-else-if="currentTask.status === 'failed'"
                  title="生成失败"
                  type="error"
                  :description="currentTask.error"
                  :closable="false"
                  show-icon
                />

                <div
                  v-else-if="currentTask.status === 'completed'"
                  class="completed-state"
                >
                  <div class="video-wrapper">
                    <video
                      :src="currentTask.video_url"
                      controls
                      class="video-element"
                    />
                  </div>
                  <div class="action-buttons">
                    <el-button type="primary" @click="downloadVideo">
                      <el-icon><Download /></el-icon>
                      下载视频
                    </el-button>
                    <el-button @click="shareVideo">
                      <el-icon><Share /></el-icon>
                      分享
                    </el-button>
                  </div>
                </div>
              </div>

              <el-empty v-else class="empty-state" description="点击生成后在此预览">
                <template #image>
                  <el-icon class="empty-icon"><VideoCamera /></el-icon>
                </template>
              </el-empty>
            </el-card>
          </el-col>
        </el-row>
        <el-row :gutter="[16, 16]">
          <!-- 生成历史 -->
          <el-card class="history-card">
            <template #header>
              <div class="card-header">
                <span>生成历史</span>
                <el-button text type="primary" size="small" @click="loadHistory">
                  <el-icon><Refresh /></el-icon>
                  刷新
                </el-button>
              </div>
            </template>
            <el-empty
              v-if="historyList.length === 0"
              description="暂无历史记录"
            />
            <div v-else class="history-grid">
              <div
                v-for="item in historyList"
                :key="item.id"
                class="history-card-item"
                @click="viewVideo(item)"
              >
                <div class="history-thumb">
                  <el-icon class="thumb-icon"><VideoCamera /></el-icon>
                </div>
                <div class="history-details">
                  <div class="history-title">{{ item.title }}</div>
                  <div class="history-footer">
                    <el-tag
                      :type="item.status === 'completed' ? 'success' : item.status === 'processing' ? 'warning' : 'danger'"
                      size="small"
                      class="status-tag"
                    >
                      {{ item.status === 'completed' ? '已完成' : item.status === 'processing' ? '生成中' : '失败' }}
                    </el-tag>
                    <span class="history-time">{{ formatTime(item.created_at) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </el-card>
        </el-row>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
// 脚本部分完全保持不变（与原始代码一致）
import { ref, reactive, onMounted, onUnmounted } from "vue";
import { ElMessage } from "element-plus";
import {
  VideoCamera,
  UploadFilled,
  Download,
  Share,
  Refresh,
} from "@element-plus/icons-vue";
import type { UploadFile } from "element-plus";
import request from "@/api/request";

interface TextForm {
  prompt: string;
  duration: number;
  aspect_ratio: string;
  style: string;
  platform?: string;
}

interface ImageForm {
  image: File | null;
  motion_prompt: string;
  duration: number;
  image_data_url?: string;
  platform?: string;
}

interface VideoTask {
  id: string;
  status: "processing" | "completed" | "failed";
  progress: number;
  estimated_time: number;
  video_url?: string;
  error?: string;
}

interface HistoryItem {
  id: number;
  title: string;
  status: string;
  created_at: string;
  video_url?: string;
}

const activeTab = ref("text");
const generating = ref(false);
const currentTask = ref<VideoTask | null>(null);
const historyList = ref<HistoryItem[]>([]);
let pollTimer: number | null = null;

// AI模式和平台选择
const aiMode = ref("API Key"); // 'API Key' 或 'Cookie'
const selectedPlatform = ref("doubao"); // 选中的平台

const textForm = reactive<TextForm>({
  prompt: "",
  duration: 10,
  aspect_ratio: "16:9",
  style: "realistic",
});

const imageForm = reactive<ImageForm>({
  image: null,
  motion_prompt: "",
  duration: 5,
});

// 处理图片上传
const handleImageChange = async (file: UploadFile) => {
  imageForm.image = file.raw as File;
  imageForm.image_data_url = await readFileAsDataUrl(file.raw as File);
};

// 生成视频
const generateVideo = async () => {
  if (activeTab.value === "text") {
    if (!textForm.prompt.trim()) {
      ElMessage.warning("请输入视频描述");
      return;
    }
  } else {
    if (!imageForm.image) {
      ElMessage.warning("请上传图片");
      return;
    }
  }

  // Cookie模式需要选择平台
  if (aiMode.value === "Cookie" && !selectedPlatform.value) {
    ElMessage.warning("请选择AI平台");
    return;
  }

  generating.value = true;
  try {
    let response;
    if (activeTab.value === "text") {
      response = await request.post("/v1/video/text-to-video", {
        text: textForm.prompt,
        background_music: false,
        subtitle: true,
        platform:
          aiMode.value === "Cookie" ? selectedPlatform.value : undefined,
      });
    } else {
      const images = imageForm.image_data_url ? [imageForm.image_data_url] : [];
      response = await request.post("/v1/video/image-to-video", {
        images,
        transition: "fade",
        duration_per_image: imageForm.duration,
        platform:
          aiMode.value === "Cookie" ? selectedPlatform.value : undefined,
      });
    }

    const task = response.data;
    currentTask.value = {
      id: task.task_id,
      status: "processing",
      progress: 0,
      estimated_time: task.estimated_time || 60,
    };

    ElMessage.success("视频生成任务已提交");
    startPolling();
    loadHistory();
  } catch (error: any) {
    ElMessage.error(error.response?.data?.message || "视频生成失败");
  } finally {
    generating.value = false;
  }
};

// 轮询任务状态
const startPolling = () => {
  if (pollTimer) {
    clearInterval(pollTimer);
  }

  pollTimer = window.setInterval(async () => {
    if (!currentTask.value) return;

    try {
      const result = await request.get(
        `/v1/video/task/${currentTask.value.id}`
      );
      const data = result.data;

      currentTask.value = {
        ...currentTask.value,
        status: data.status,
        progress: data.progress || 0,
        estimated_time: data.estimated_time || 0,
        video_url: data.video_url,
        error: data.error,
      };

      if (data.status === "completed" || data.status === "failed") {
        stopPolling();
        if (data.status === "completed") {
          ElMessage.success("视频生成完成");
          loadHistory();
        } else {
          ElMessage.error("视频生成失败");
        }
      }
    } catch (error) {
      console.error("获取任务状态失败", error);
    }
  }, 3000);
};

const readFileAsDataUrl = (file: File) =>
  new Promise<string>((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result as string);
    reader.onerror = () => reject(new Error("读取图片失败"));
    reader.readAsDataURL(file);
  });

const stopPolling = () => {
  if (pollTimer) {
    clearInterval(pollTimer);
    pollTimer = null;
  }
};

// 查看视频
const viewVideo = (item: HistoryItem) => {
  if (item.status === "completed" && item.video_url) {
    currentTask.value = {
      id: item.id.toString(),
      status: "completed",
      progress: 100,
      estimated_time: 0,
      video_url: item.video_url,
    };
  }
};

// 下载视频
const downloadVideo = () => {
  if (currentTask.value?.video_url) {
    const link = document.createElement("a");
    link.href = currentTask.value.video_url;
    link.download = `ai-video-${Date.now()}.mp4`;
    link.click();
  }
};

// 分享视频
const shareVideo = async () => {
  if (!currentTask.value?.video_url) {
    ElMessage.warning("暂无可分享的视频链接");
    return;
  }

  try {
    await navigator.clipboard.writeText(currentTask.value.video_url);
    ElMessage.success("视频链接已复制，可直接分享");
  } catch (error) {
    ElMessage.warning("复制失败，请手动复制链接");
  }
};

// 加载历史记录
const loadHistory = async () => {
  try {
    const response = await request.get("/v1/creations", {
      params: {
        content_type: "video",
        skip: 0,
        limit: 10,
      },
    });
    historyList.value = response.items;
  } catch (error) {
    console.error("加载历史记录失败", error);
  }
};

// 格式化时间
const formatTime = (time: string) => {
  const date = new Date(time);
  const now = new Date();
  const diff = now.getTime() - date.getTime();

  if (diff < 60000) return "刚刚";
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`;
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`;
  return date.toLocaleDateString();
};

onMounted(() => {
  loadHistory();
});

onUnmounted(() => {
  stopPolling();
});
</script>

<style scoped lang="scss">
// Variables (保持不变)
$primary-color: #409eff;
$success-color: #67c23a;
$border-color: #edf2f7;
$bg-color: #f8fbff;
$text-primary: #1f2937;
$text-secondary: #606266;
$text-tertiary: #909399;
$shadow-light: 0 8px 24px rgba(15, 23, 42, 0.04);
$shadow-hover: 0 12px 32px rgba(15, 23, 42, 0.08);
$border-radius-lg: 14px;
$border-radius-md: 12px;
$border-radius-sm: 10px;
$transition: all 0.3s ease-out;

.video-generation {
  padding: 20px;
  background: linear-gradient(180deg, $bg-color 0%, #ffffff 40%);
  min-height: 100vh;
  --hero-from: rgba(59, 130, 246, 0.18);
  --hero-to: rgba(14, 165, 233, 0.18);
  --page-accent: #2563eb;

  // 精简英雄区域高度
  .page-hero {
    padding: 16px 0; // 显著减少上下内边距
    min-height: auto;

    .hero-grid {
      grid-template-columns: minmax(0, 0.6fr) minmax(0, 1.1fr); // 优化比例
      gap: 16px; // 减小间距
      align-items: center;
      padding: 12px;

      .hero-content {
        h1 {
          margin: 6px 0 4px; // 紧凑标题间距
          font-size: clamp(22px, 4.5vw, 28px); // 稍微缩小最大字号
          font-weight: 700;
          color: $text-primary;
          letter-spacing: -0.4px;
        }
        .hero-subtitle {
          margin: 0;
          font-size: clamp(13px, 2vw, 14px); // 稍微缩小
          color: $text-tertiary;
          line-height: 1.6;
        }
      }

      .hero-panel {
        padding: 14px; // 减小内边距
        border-radius: 16px;
        background: rgba(255, 255, 255, 0.85);
        border: 1px solid rgba(37, 99, 235, 0.1);
        box-shadow: $shadow-light;
        backdrop-filter: blur(10px);

        // 双栏布局容器
        .hero-panel-row {
          display: flex;
          gap: 14px;

          // 响应式：小屏堆叠
          @media (max-width: 768px) {
            flex-direction: column;
          }
        }

        // 每个面板区块
        .hero-panel-section {
          flex: 1;
          min-width: 0;

          .section-title {
            font-size: 13px;
            font-weight: 600;
            color: #1f2937;
            margin-bottom: 8px;
            padding-bottom: 5px;
            border-bottom: 1px solid rgba(0, 0, 0, 0.06);
          }
        }

        // 紧凑型信息列表
        .info-list.compact {
          display: flex;
          flex-direction: column;
          gap: 7px; // 减小项间距

          .info-item {
            padding: 7px 9px; // 减小内边距
            border-radius: 10px;
            background: rgba(249, 250, 251, 0.7);
            border: 1px solid rgba(0, 0, 0, 0.03);
            display: flex;
            align-items: flex-start;
            gap: 9px;

            .info-icon {
              width: 28px;
              height: 28px;
              border-radius: 10px;
              display: flex;
              align-items: center;
              justify-content: center;
              background: rgba(37, 99, 235, 0.1);
              color: #2563eb;
              flex-shrink: 0;

              .el-icon {
                font-size: 16px; // 稍微缩小图标
              }
            }

            .info-text {
              flex: 1;
              min-width: 0;

              .info-title {
                font-size: 12px;
                font-weight: 500;
                margin-bottom: 1px;
                color: #1f2937;
              }
              .info-desc {
                font-size: 11px;
                color: $text-tertiary;
                line-height: 1.4;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
              }
            }
          }
        }
      }
    }
  }

  // 调整dashboard与英雄区域间距
  .page-dashboard {
    margin-top: 16px;
  }

  // 以下样式保持与原始代码一致（仅保留关键部分，完整样式请参考原始代码）
  :deep(.el-card) {
    border-radius: $border-radius-lg;
    border: 1px solid $border-color;
    box-shadow: $shadow-light;
    transition: $transition;

    &:hover {
      box-shadow: $shadow-hover;
    }

    .el-card__header {
      padding: 16px 20px;
      border-bottom: 1px solid $border-color;
      background: #f9fafb;
    }

    .el-card__body {
      padding: 20px;
    }
  }

  :deep(.el-form-item) {
    margin-bottom: 16px;

    &:last-child {
      margin-bottom: 0;
    }
  }

  :deep(.el-input) {
    &.is-disabled {
      .el-input__wrapper {
        background-color: #f5f7fa;
      }
    }
  }

  :deep(.el-tabs) {
    .el-tabs__header {
      margin-bottom: 16px;
    }

    .el-tabs__nav {
      border-bottom: 2px solid $border-color;
    }

    .el-tabs__item {
      color: $text-secondary;
      border-color: transparent;

      &.is-active {
        color: $primary-color;
      }

      &:hover {
        color: $primary-color;
      }
    }
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
    gap: 12px;
    flex-wrap: wrap;

    span {
      font-size: 16px;
      font-weight: 500;
      color: $text-primary;
      white-space: nowrap;
    }

    :deep(.el-button) {
      white-space: nowrap;
    }
  }

  .input-card {
    margin-bottom: 20px;
    transition: $transition;

    :deep(.custom-tabs) {
      .el-tabs__header {
        margin-bottom: 20px;
      }
    }

    .model-card {
      margin-top: 20px;
      background-color: #f9fafb;

      :deep(.el-card__header) {
        background-color: transparent;
        padding: 12px 0;
      }

      :deep(.el-card__body) {
        padding: 16px 0;
      }

      :deep(.el-alert) {
        margin-top: 12px;
        border-radius: 8px;
      }
    }
  }

  // Preview Card
  .preview-card {
    margin-bottom: 20px;
    transition: $transition;

    .result-content {
      min-height: 280px;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .empty-state {
      min-height: 280px;

      .empty-icon {
        font-size: 64px;
        color: $text-tertiary;
        opacity: 0.5;
      }
    }

    .generating-state {
      padding: 32px 16px;
      text-align: center;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 16px;

      .progress-circle {
        display: flex;
        justify-content: center;
      }

      .progress-text {
        margin: 0;
        font-size: 16px;
        font-weight: 500;
        color: $text-primary;
      }

      .progress-hint {
        margin: 0;
        font-size: 13px;
        color: $text-tertiary;
      }
    }

    .completed-state {
      .video-wrapper {
        background: #000;
        border-radius: $border-radius-md;
        overflow: hidden;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);

        .video-element {
          width: 100%;
          max-height: 400px;
          display: block;
        }
      }

      .action-buttons {
        margin-top: 16px;
        display: flex;
        gap: 12px;
        justify-content: center;

        :deep(.el-button) {
          min-width: 110px;
        }
      }
    }

    :deep(.el-alert) {
      border-radius: 8px;
    }
  }

  // History Card
  .history-card {
    margin-bottom: 0;

    .history-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
      gap: 12px;
      padding: 4px 0;
    }

    .history-card-item {
      display: flex;
      flex-direction: column;
      background: #fff;
      border: 1px solid $border-color;
      border-radius: $border-radius-md;
      overflow: hidden;
      cursor: pointer;
      transition: $transition;

      &:hover {
        border-color: $primary-color;
        box-shadow: 0 4px 12px rgba(64, 158, 255, 0.12);
        transform: translateY(-2px);
      }

      .history-thumb {
        height: 100px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #f0f4ff 0%, #e8edf5 100%);

        .thumb-icon {
          font-size: 40px;
          color: $primary-color;
        }
      }

      .history-details {
        padding: 12px;

        .history-title {
          font-size: 13px;
          color: $text-primary;
          font-weight: 500;
          margin-bottom: 8px;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .history-footer {
          display: flex;
          align-items: center;
          justify-content: space-between;

          .status-tag {
            border-radius: 4px;
            font-size: 11px;
          }

          .history-time {
            font-size: 12px;
            color: $text-tertiary;
          }
        }
      }
    }
  }

  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateY(8px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  @keyframes slideInLeft {
    from {
      opacity: 0;
      transform: translateX(-12px);
    }
    to {
      opacity: 1;
      transform: translateX(0);
    }
  }
}

// 响应式设计（保持原始响应式结构，仅微调英雄区域）
@media (max-width: 1024px) {
  .video-generation {
    padding: 16px;

    .page-hero {
      padding: 12px 0;

      .hero-grid {
        gap: 12px;

        .hero-content {
          h1 {
            font-size: clamp(20px, 4vw, 26px);
          }
        }

        .hero-panel {
          padding: 12px;

          .hero-panel-row {
            gap: 10px;
          }

          .hero-panel-section {
            .section-title {
              font-size: 12px;
              margin-bottom: 6px;
            }
          }

          .info-list.compact {
            gap: 6px;

            .info-item {
              padding: 6px 8px;
              gap: 8px;

              .info-icon {
                width: 26px;
                height: 26px;
                font-size: 15px;
              }

              .info-text {
                .info-title {
                  font-size: 11.5px;
                }
                .info-desc {
                  font-size: 10.5px;
                }
              }
            }
          }
        }
      }
    }

    .header-card {
      margin-bottom: 20px;

      .header-content {
        padding: 20px 12px;
      }
    }

    .video-player {
      .video-element {
        max-height: 400px;
      }
    }

    .history-list {
      max-height: 350px;
    }
  }
}

@media (max-width: 768px) {
  .video-generation {
    padding: 12px;
    background: linear-gradient(180deg, $bg-color 0%, #ffffff 60%);

    :deep(.el-card) {
      border-radius: 12px;

      .el-card__header {
        padding: 14px 16px;
      }

      .el-card__body {
        padding: 16px;
      }
    }

    .card-header {
      gap: 8px;

      span {
        font-size: 15px;
      }

      :deep(.el-button) {
        padding: 6px 12px;
        font-size: 13px;
      }
    }

    .input-card {
      margin-bottom: 16px;

      :deep(.el-form-item) {
        margin-bottom: 14px;
      }

      .model-card {
        margin-top: 16px;
      }
    }

    .preview-card {
      margin-bottom: 16px;

      .completed-state {
        .video-wrapper {
          .video-element {
            max-height: 300px;
          }
        }

        .action-buttons {
          gap: 8px;
          margin-top: 16px;

          :deep(.el-button) {
            flex: 1;
            min-width: 100px;
            padding: 8px 12px;
            font-size: 13px;
          }
        }
      }

      .generating-state {
        padding: 24px 12px;
        gap: 12px;
      }
    }

    .history-card {
      margin-top: 0;

      .history-grid {
        grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
        gap: 10px;

        .history-card-item {
          .history-thumb {
            height: 80px;

            .thumb-icon {
              font-size: 32px;
            }
          }

          .history-details {
            padding: 10px;

            .history-title {
              font-size: 12px;
              margin-bottom: 6px;
            }
          }
        }
      }
    }
  }
}

@media (max-width: 480px) {
  .video-generation {
    padding: 8px;

    :deep(.el-card) {
      border-radius: 10px;
      border: 1px solid $border-color;

      .el-card__header {
        padding: 12px 14px;
      }

      .el-card__body {
        padding: 14px;
      }
    }

    .card-header {
      flex-direction: column;
      align-items: flex-start;
      gap: 10px;

      span {
        font-size: 14px;
      }

      :deep(.el-button) {
        width: 100%;
        padding: 6px 12px;
        font-size: 12px;
      }
    }

    :deep(.el-form-item) {
      margin-bottom: 12px;

      :deep(.el-form-item__label) {
        font-size: 13px;
        padding-bottom: 8px;
      }
    }

    :deep(.el-input) {
      :deep(.el-input__wrapper) {
        padding: 6px 10px;
      }

      :deep(textarea) {
        font-size: 13px;
        padding: 6px;
      }
    }

    :deep(.el-select) {
      :deep(.el-input) {
        font-size: 13px;
      }
    }

    :deep(.el-tabs) {
      :deep(.el-tabs__header) {
        margin-bottom: 12px;
      }

      :deep(.el-tabs__item) {
        font-size: 13px;
        padding: 0 12px;
      }

      :deep(.el-tabs__content) {
        padding: 0;
      }
    }

    .input-card {
      margin-bottom: 12px;

      .model-card {
        margin-top: 12px;
      }
    }

    .preview-card {
      margin-bottom: 12px;

      .generating-state {
        padding: 20px 8px;
        gap: 10px;

        .progress-text {
          font-size: 14px;
        }

        .progress-hint {
          font-size: 12px;
        }
      }

      .completed-state {
        .video-wrapper {
          .video-element {
            max-height: 240px;
            border-radius: 8px;
          }
        }

        .action-buttons {
          flex-direction: column;
          gap: 8px;
          margin-top: 12px;

          :deep(.el-button) {
            width: 100%;
            padding: 8px 12px;
            font-size: 12px;
          }
        }
      }

      .empty-state {
        min-height: 200px;

        .empty-icon {
          font-size: 48px;
        }
      }
    }

    .history-card {
      .history-grid {
        grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
        gap: 8px;

        .history-card-item {
          .history-thumb {
            height: 70px;

            .thumb-icon {
              font-size: 28px;
            }
          }

          .history-details {
            padding: 8px;

            .history-title {
              font-size: 11px;
              margin-bottom: 4px;
            }

            .history-footer {
              .status-tag {
                font-size: 10px;
              }

              .history-time {
                font-size: 10px;
              }
            }
          }
        }
      }
    }
  }
}

@media (max-width: 320px) {
  .video-generation {
    padding: 6px;

    :deep(.el-card) {
      border-radius: 8px;

      .el-card__header {
        padding: 10px 12px;
      }

      .el-card__body {
        padding: 12px;
      }
    }

    .video-player {
      .video-element {
        max-height: 200px;
      }
    }
  }
}
</style>
