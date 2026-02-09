<template>
  <div class="ppt-generation flagship-page page-shell">
    <section class="page-hero ppt-hero">
      <div class="hero-grid">
        <div class="hero-content">
          <h1>AI PPT生成</h1>
          <p class="hero-subtitle">使用AI技术，快速生成专业PPT演示文稿</p>
        </div>
        <div class="hero-panel">
          <div class="hero-panel-row">
            <div class="hero-panel-section">
              <div class="section-title">演示建议</div>
              <div class="info-list compact">
                <div class="info-item">
                  <div class="info-icon">
                    <el-icon><Document /></el-icon>
                  </div>
                  <div class="info-text">
                    <div class="info-title">聚焦主题</div>
                    <div class="info-desc">用一句话概括PPT核心价值</div>
                  </div>
                </div>
                <div class="info-item">
                  <div class="info-icon">
                    <el-icon><View /></el-icon>
                  </div>
                  <div class="info-text">
                    <div class="info-title">控制页数</div>
                    <div class="info-desc">突出重点信息，保持节奏紧凑</div>
                  </div>
                </div>
              </div>
            </div>
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
                    <div class="info-title">当前风格</div>
                    <div class="info-desc">
                      {{ activeTab === "theme" ? themeForm.style : "自定义" }}
                    </div>
                  </div>
                </div>
                <div class="info-item">
                  <div class="info-text">
                    <div class="info-title">计划页数</div>
                    <div class="info-desc">
                      {{ activeTab === "theme" ? themeForm.pages : "自定义" }}
                      页
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="page-dashboard">
      <div class="dashboard-grid">
        <div class="dashboard-card">
          <div class="label">生成方式</div>
          <div class="value">
            {{ activeTab === "theme" ? "主题生成" : "大纲生成" }}
          </div>
          <div class="delta">快速构建演示结构</div>
        </div>
        <div class="dashboard-card">
          <div class="label">计划页数</div>
          <div class="value">
            {{ activeTab === "theme" ? themeForm.pages : "自定义" }}
          </div>
          <div class="delta">适配不同演示节奏</div>
        </div>
        <div class="dashboard-card">
          <div class="label">任务状态</div>
          <div class="value">
            {{ currentPPT ? currentPPT.status : "待生成" }}
          </div>
          <div class="delta">生成完成即可下载预览</div>
        </div>
      </div>
    </section>

    <section class="page-body">
      <div class="main-panel">
        <el-row :gutter="[16, 16]">
          <el-col :xs="24" :sm="24" :md="24" :lg="12">
            <el-card class="input-card">
              <template #header>
                <div class="card-header">
                  <span>PPT生成</span>
                  <el-button
                    type="primary"
                    :loading="generating"
                    @click="generatePPT"
                  >
                    <el-icon><Document /></el-icon>
                    生成PPT
                  </el-button>
                </div>
              </template>

              <el-tabs v-model="activeTab" class="custom-tabs">
                <el-tab-pane label="主题生成" name="theme">
                  <el-form :model="themeForm" label-position="top">
                    <el-form-item label="PPT主题" required>
                      <el-input
                        v-model="themeForm.theme"
                        placeholder="例如：人工智能在教育领域的应用"
                        maxlength="100"
                        show-word-limit
                      />
                    </el-form-item>
                    <el-form-item label="页数">
                      <el-slider
                        v-model="themeForm.pages"
                        :min="5"
                        :max="30"
                        :marks="{ 5: '5', 15: '15', 30: '30' }"
                      />
                    </el-form-item>
                    <el-form-item label="风格">
                      <el-select v-model="themeForm.style">
                        <el-option label="商务" value="business" />
                        <el-option label="简约" value="simple" />
                        <el-option label="创意" value="creative" />
                      </el-select>
                    </el-form-item>
                  </el-form>
                </el-tab-pane>

                <el-tab-pane label="大纲生成" name="outline">
                  <el-form :model="outlineForm" label-position="top">
                    <el-form-item label="PPT大纲" required>
                      <el-input
                        v-model="outlineForm.outline"
                        type="textarea"
                        :rows="12"
                        placeholder="请输入PPT大纲，每行一个要点"
                        maxlength="2000"
                        show-word-limit
                      />
                    </el-form-item>
                  </el-form>
                </el-tab-pane>
              </el-tabs>

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
                      <el-option label="Claude" value="claude" />
                    </el-select>
                  </el-form-item>
                  <el-alert type="success" title="Cookie模式" :closable="false">
                    <p>使用已授权账号的免费额度</p>
                  </el-alert>
                </template>
              </el-card>
            </el-card>
          </el-col>

          <el-col :xs="24" :sm="24" :md="24" :lg="12">
            <el-card class="preview-card">
              <template #header>
                <div class="card-header">
                  <span>生成结果</span>
                  <el-tag
                    v-if="currentPPT && currentPPT.status === 'processing'"
                    type="warning"
                  >
                    生成中 {{ currentPPT.progress }}%
                  </el-tag>
                  <el-tag
                    v-else-if="currentPPT && currentPPT.status === 'completed'"
                    type="success"
                  >
                    已完成
                  </el-tag>
                </div>
              </template>
              <el-empty
                v-if="!currentPPT"
                class="empty-state"
                description="点击生成后查看结果"
              >
                <template #image>
                  <el-icon class="empty-icon"><Document /></el-icon>
                </template>
              </el-empty>
              <div v-else class="result-content">
                <div
                  v-if="currentPPT.status === 'processing'"
                  class="generating-state"
                >
                  <div class="progress-circle">
                    <el-progress
                      type="circle"
                      :percentage="currentPPT.progress"
                      :width="100"
                    />
                  </div>
                  <p class="progress-text">PPT生成中...</p>
                </div>
                <div
                  v-else-if="currentPPT.status === 'completed'"
                  class="completed-state"
                >
                  <div class="result-info">
                    <el-icon class="success-icon"><SuccessFilled /></el-icon>
                    <p>PPT已生成完成</p>
                  </div>
                  <div class="action-buttons">
                    <el-button type="primary" @click="downloadPPT">
                      <el-icon><Download /></el-icon>
                      下载PPT
                    </el-button>
                    <el-button @click="previewPPT">
                      <el-icon><View /></el-icon>
                      在线预览
                    </el-button>
                  </div>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onUnmounted } from "vue";
import { ElMessage } from "element-plus";
import {
  Document,
  Download,
  View,
  SuccessFilled,
} from "@element-plus/icons-vue";
import request from "@/api/request";

const activeTab = ref("theme");
const generating = ref(false);
const currentPPT = ref<any>(null);

const aiMode = ref("API Key");
const selectedPlatform = ref("doubao");

const themeForm = reactive({
  theme: "",
  pages: 10,
  style: "business",
});

const outlineForm = reactive({
  outline: "",
});

const currentTaskId = ref<string | null>(null);
let pollTimer: number | null = null;

const generatePPT = async () => {
  if (activeTab.value === "theme" && !themeForm.theme.trim()) {
    ElMessage.warning("请输入PPT主题");
    return;
  }
  if (activeTab.value === "outline" && !outlineForm.outline.trim()) {
    ElMessage.warning("请输入PPT大纲");
    return;
  }

  if (aiMode.value === "Cookie" && !selectedPlatform.value) {
    ElMessage.warning("请选择AI平台");
    return;
  }

  generating.value = true;
  try {
    let result;
    if (activeTab.value === "theme") {
      result = await request.post("/v1/ppt/generate", {
        topic: themeForm.theme,
        slides_count: themeForm.pages,
        style: themeForm.style,
        platform:
          aiMode.value === "Cookie" ? selectedPlatform.value : undefined,
      });
    } else {
      result = await request.post("/v1/ppt/from-outline", {
        outline: outlineForm.outline,
        platform:
          aiMode.value === "Cookie" ? selectedPlatform.value : undefined,
      });
    }
    const task = result.data;
    currentTaskId.value = task.task_id;
    currentPPT.value = null;
    ElMessage.success("PPT生成任务已提交");
    startPolling();
  } catch (error: any) {
    ElMessage.error(error.response?.data?.message || "PPT生成失败");
  } finally {
    generating.value = false;
  }
};

const downloadPPT = () => {
  if (currentPPT.value?.ppt_url) {
    window.open(currentPPT.value.ppt_url);
  }
};

const previewPPT = () => {
  if (currentPPT.value?.ppt_url) {
    window.open(currentPPT.value.ppt_url, "_blank");
    return;
  }
  ElMessage.warning("暂无可预览的PPT文件");
};

const startPolling = () => {
  if (!currentTaskId.value) return;
  if (pollTimer) {
    clearInterval(pollTimer);
  }
  pollTimer = window.setInterval(async () => {
    if (!currentTaskId.value) return;
    try {
      const result = await request.get(`/v1/ppt/task/${currentTaskId.value}`);
      const task = result.data;
      if (task.status === "completed") {
        currentPPT.value = task;
        stopPolling();
        ElMessage.success("PPT生成完成");
      } else if (task.status === "failed") {
        stopPolling();
        ElMessage.error("PPT生成失败");
      }
    } catch (error) {
      console.error("获取PPT任务状态失败", error);
    }
  }, 3000);
};

const stopPolling = () => {
  if (pollTimer) {
    clearInterval(pollTimer);
    pollTimer = null;
  }
};

onUnmounted(() => {
  stopPolling();
});
</script>

<style scoped lang="scss">
// Variables
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

.ppt-generation {
  padding: 20px;
  background: linear-gradient(180deg, $bg-color 0%, #ffffff 40%);
  min-height: 100vh;
  --hero-from: rgba(59, 130, 246, 0.18);
  --hero-to: rgba(139, 92, 246, 0.18);
  --page-accent: #4f46e5;

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

  :deep(.el-select) {
    width: 100%;
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

  :deep(.el-input) {
    &.is-disabled {
      .el-input__wrapper {
        background-color: #f5f7fa;
      }
    }
  }

  // Page Hero
  .page-hero {
    padding: 16px 0;
    min-height: auto;
  }

  // Hero Grid
  .hero-grid {
    position: relative;
    z-index: 1;
    grid-template-columns: minmax(0, 0.6fr) minmax(0, 1.1fr);
    gap: 16px;
    align-items: center;
    padding: 12px;
  }

  .hero-content {
    h1 {
      margin: 12px 0 10px;
      font-size: clamp(22px, 4vw, 30px);
      font-weight: 700;
      color: $text-primary;
      letter-spacing: -0.4px;
    }

    .hero-subtitle {
      margin: 0;
      font-size: clamp(12px, 2vw, 14px);
      color: $text-tertiary;
      line-height: 1.6;
    }

    .hero-panel {
      padding: 14px;
      border-radius: 16px;
      background: rgba(255, 255, 255, 0.85);
      border: 1px solid rgba(37, 99, 235, 0.1);
      box-shadow: $shadow-light;
      backdrop-filter: blur(10px);

      .hero-panel-row {
        display: flex;
        gap: 14px;

        @media (max-width: 768px) {
          flex-direction: column;
        }
      }

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

      .info-list.compact {
        display: flex;
        flex-direction: column;
        gap: 7px;

        .info-item {
          padding: 7px 9px;
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
              font-size: 16px;
            }
          }

          .info-text {
            flex: 1;
            min-width: 0;

            .info-title {
              font-size: 12px;
              font-weight: 600;
              color: #1f2937;
              margin-bottom: 2px;
            }

            .info-desc {
              font-size: 11px;
              color: $text-tertiary;
              line-height: 1.4;
            }
          }
        }
      }
    }

    // Card Header
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

    // Input Card
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
      }

      .completed-state {
        padding: 24px 16px;

        .result-info {
          text-align: center;
          margin-bottom: 20px;

          .success-icon {
            font-size: 48px;
            color: $success-color;
            margin-bottom: 12px;
          }

          p {
            margin: 0;
            font-size: 16px;
            font-weight: 500;
            color: $text-primary;
          }
        }

        .action-buttons {
          display: flex;
          gap: 12px;
          justify-content: center;

          :deep(.el-button) {
            min-width: 110px;
          }
        }
      }
    }

    // Animations
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
  }

  // Responsive Design - Tablet (768px - 1024px)
  @media (max-width: 1024px) {
    .ppt-generation {
      padding: 16px;
    }
  }

  // Responsive Design - Large Mobile (480px - 768px)
  @media (max-width: 768px) {
    .ppt-generation {
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

      .hero-grid {
        grid-template-columns: 1fr;
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

        .generating-state {
          padding: 24px 12px;
          gap: 12px;
        }

        .completed-state {
          padding: 20px 12px;

          .result-info {
            margin-bottom: 16px;

            .success-icon {
              font-size: 40px;
            }

            p {
              font-size: 14px;
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
      }
    }
  }

  // Responsive Design - Small Mobile (320px - 480px)
  @media (max-width: 480px) {
    .ppt-generation {
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
        }

        .completed-state {
          padding: 20px 12px;

          .result-info {
            margin-bottom: 16px;

            .success-icon {
              font-size: 40px;
            }

            p {
              font-size: 14px;
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
    }
  }

  .ppt-preview {
    .ppt-actions {
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

  // Ultra Small Mobile (< 320px)
  @media (max-width: 320px) {
    .ppt-generation {
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
    }
  }
}
</style>
