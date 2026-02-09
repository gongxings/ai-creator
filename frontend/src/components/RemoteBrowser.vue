<template>
  <el-dialog
    v-model="visible"
    :title="`${platformName} 授权登录`"
    width="900px"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    @closed="handleClosed"
  >
    <div class="remote-browser">
      <!-- 状态提示 -->
      <div class="status-bar" :class="statusClass">
        <el-icon v-if="status === 'connecting'" class="is-loading"><Loading /></el-icon>
        <el-icon v-else-if="status === 'completed'"><SuccessFilled /></el-icon>
        <el-icon v-else-if="status === 'error'"><CircleCloseFilled /></el-icon>
        <el-icon v-else><Monitor /></el-icon>
        <span>{{ statusMessage }}</span>
      </div>

      <!-- 浏览器视图 -->
      <div 
        class="browser-viewport"
        ref="viewportRef"
        @mousedown="handleMouseDown"
        @mouseup="handleMouseUp"
        @mousemove="handleMouseMove"
        @click="handleClick"
        @dblclick="handleDblClick"
        @wheel="handleWheel"
        @contextmenu.prevent="handleContextMenu"
      >
        <img 
          v-if="screenshot"
          :src="`data:image/jpeg;base64,${screenshot}`"
          class="screenshot"
          draggable="false"
          @load="onImageLoad"
        />
        <div v-else class="loading-placeholder">
          <el-icon class="is-loading" :size="48"><Loading /></el-icon>
          <p>正在加载浏览器画面...</p>
        </div>

        <!-- 点击反馈 -->
        <div 
          v-if="clickFeedback.visible"
          class="click-feedback"
          :style="{ left: clickFeedback.x + 'px', top: clickFeedback.y + 'px' }"
        />
      </div>

      <!-- 键盘输入区域 -->
      <div class="keyboard-input" v-if="status === 'waiting_login'">
        <el-input
          v-model="keyboardText"
          placeholder="在此输入文字，然后按 Enter 发送到浏览器..."
          @keydown.enter="sendKeyboardText"
          clearable
        >
          <template #append>
            <el-button @click="sendKeyboardText">发送</el-button>
          </template>
        </el-input>
        <div class="keyboard-hint">
          提示: 点击上方浏览器画面可进行鼠标操作，输入框内输入文字后按回车发送
        </div>
      </div>

      <!-- 操作按钮 -->
      <div class="actions">
        <el-button v-if="status === 'completed'" type="primary" @click="handleComplete">
          完成
        </el-button>
        <el-button v-else @click="handleCancel">取消</el-button>
      </div>
    </div>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Loading, SuccessFilled, CircleCloseFilled, Monitor } from '@element-plus/icons-vue'
import { useUserStore } from '@/store/user'

interface Props {
  modelValue: boolean
  platform: string
  platformName?: string
  /** 平台类型: oauth (AI平台) 或 publish (发布平台) */
  platformType?: 'oauth' | 'publish'
  /** 发布平台账号名称 (仅 platformType='publish' 时使用) */
  accountName?: string
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'success', credentials: any): void
  (e: 'cancel'): void
}

const props = withDefaults(defineProps<Props>(), {
  platformName: '平台',
  platformType: 'oauth',
  accountName: 'default',
})

const emit = defineEmits<Emits>()

const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
})

// 状态
type Status = 'connecting' | 'starting' | 'navigating' | 'waiting_login' | 'logged_in' | 'extracting' | 'completed' | 'error' | 'closed'
const status = ref<Status>('connecting')
const statusMessage = ref('正在连接...')
const screenshot = ref<string | null>(null)
const credentials = ref<any>(null)
const keyboardText = ref('')

// WebSocket
let ws: WebSocket | null = null

// 点击反馈
const clickFeedback = ref({ visible: false, x: 0, y: 0 })
let clickFeedbackTimer: number | null = null

// 视口引用
const viewportRef = ref<HTMLDivElement | null>(null)

// 状态样式
const statusClass = computed(() => {
  switch (status.value) {
    case 'completed':
      return 'status-success'
    case 'error':
      return 'status-error'
    case 'waiting_login':
      return 'status-warning'
    default:
      return 'status-info'
  }
})

// 连接 WebSocket
const connect = () => {
  const userStore = useUserStore()
  const token = userStore.token || localStorage.getItem('token')
  if (!token) {
    status.value = 'error'
    statusMessage.value = '未登录，请先登录'
    return
  }

  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const host = window.location.host
  
  // 根据平台类型选择不同的 WebSocket 端点
  let wsUrl: string
  if (props.platformType === 'publish') {
    wsUrl = `${protocol}//${host}/api/v1/publish-remote-browser/ws/${props.platform}?token=${token}&account_name=${encodeURIComponent(props.accountName)}`
  } else {
    // OAuth 平台也需要传递 account_name
    wsUrl = `${protocol}//${host}/api/v1/remote-browser/ws/${props.platform}?token=${token}&account_name=${encodeURIComponent(props.accountName)}`
  }

  console.log('Connecting to WebSocket:', wsUrl)
  status.value = 'connecting'
  statusMessage.value = '正在连接服务器...'

  ws = new WebSocket(wsUrl)

  ws.onopen = () => {
    console.log('WebSocket connected')
    status.value = 'starting'
    statusMessage.value = '已连接，正在启动浏览器...'
  }

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      handleMessage(data)
    } catch (e) {
      console.error('Failed to parse message:', e)
    }
  }

  ws.onerror = (error) => {
    console.error('WebSocket error:', error)
    status.value = 'error'
    statusMessage.value = '连接错误'
  }

  ws.onclose = (event) => {
    console.log('WebSocket closed:', event.code, event.reason)
    if (status.value !== 'completed' && status.value !== 'error') {
      status.value = 'closed'
      statusMessage.value = '连接已断开'
    }
  }
}

// 处理服务端消息
const handleMessage = (data: any) => {
  switch (data.type) {
    case 'screenshot':
      screenshot.value = data.data
      break

    case 'status':
      status.value = data.status as Status
      statusMessage.value = data.data?.message || getStatusMessage(data.status)
      break

    case 'credentials':
      status.value = 'completed'
      statusMessage.value = data.data?.message || '授权成功！'
      credentials.value = data.data
      ElMessage.success('登录成功，Cookie已自动保存')
      break

    case 'error':
      status.value = 'error'
      statusMessage.value = data.data?.message || '发生错误'
      ElMessage.error(statusMessage.value)
      break
  }
}

// 获取状态消息
const getStatusMessage = (s: string): string => {
  const messages: Record<string, string> = {
    starting: '正在启动浏览器...',
    navigating: '正在打开登录页面...',
    waiting_login: '请在上方完成登录操作',
    logged_in: '检测到登录成功！',
    extracting: '正在提取Cookie...',
    completed: '授权完成！',
    error: '发生错误',
    closed: '连接已断开',
  }
  return messages[s] || s
}

// 发送消息到服务端
const sendMessage = (msg: any) => {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify(msg))
  }
}

// 获取相对坐标（0-1）
const getRelativeCoords = (event: MouseEvent): { x: number; y: number } | null => {
  const viewport = viewportRef.value
  if (!viewport) return null

  const rect = viewport.getBoundingClientRect()
  const x = (event.clientX - rect.left) / rect.width
  const y = (event.clientY - rect.top) / rect.height

  return {
    x: Math.max(0, Math.min(1, x)),
    y: Math.max(0, Math.min(1, y)),
  }
}

// 显示点击反馈
const showClickFeedback = (event: MouseEvent) => {
  const viewport = viewportRef.value
  if (!viewport) return

  const rect = viewport.getBoundingClientRect()
  clickFeedback.value = {
    visible: true,
    x: event.clientX - rect.left,
    y: event.clientY - rect.top,
  }

  if (clickFeedbackTimer) {
    clearTimeout(clickFeedbackTimer)
  }
  clickFeedbackTimer = window.setTimeout(() => {
    clickFeedback.value.visible = false
  }, 300)
}

// 鼠标事件处理
const handleClick = (event: MouseEvent) => {
  const coords = getRelativeCoords(event)
  if (!coords) return

  showClickFeedback(event)
  sendMessage({
    type: 'mouse',
    event: 'click',
    x: coords.x,
    y: coords.y,
    button: 'left',
  })
}

const handleDblClick = (event: MouseEvent) => {
  const coords = getRelativeCoords(event)
  if (!coords) return

  sendMessage({
    type: 'mouse',
    event: 'dblclick',
    x: coords.x,
    y: coords.y,
    button: 'left',
  })
}

const handleMouseDown = (event: MouseEvent) => {
  // 可选: 实现拖拽
}

const handleMouseUp = (event: MouseEvent) => {
  // 可选: 实现拖拽
}

const handleMouseMove = (event: MouseEvent) => {
  // 可选: 实现鼠标移动（可能会产生大量消息）
}

const handleWheel = (event: WheelEvent) => {
  event.preventDefault()
  sendMessage({
    type: 'scroll',
    deltaX: event.deltaX,
    deltaY: event.deltaY,
  })
}

const handleContextMenu = (event: MouseEvent) => {
  const coords = getRelativeCoords(event)
  if (!coords) return

  sendMessage({
    type: 'mouse',
    event: 'click',
    x: coords.x,
    y: coords.y,
    button: 'right',
  })
}

// 发送键盘文本
const sendKeyboardText = () => {
  if (!keyboardText.value) return

  sendMessage({
    type: 'keyboard',
    event: 'type',
    text: keyboardText.value,
  })

  keyboardText.value = ''
}

// 图片加载完成
const onImageLoad = () => {
  // 可以在这里调整视口大小
}

// 完成
const handleComplete = () => {
  emit('success', credentials.value)
  visible.value = false
}

// 取消
const handleCancel = () => {
  sendMessage({ type: 'close' })
  emit('cancel')
  visible.value = false
}

// 关闭处理
const handleClosed = () => {
  if (ws) {
    ws.close()
    ws = null
  }
  screenshot.value = null
  status.value = 'connecting'
  statusMessage.value = '正在连接...'
  credentials.value = null
}

// 监听显示状态
watch(visible, (newVal) => {
  if (newVal) {
    connect()
  }
})

// 清理
onUnmounted(() => {
  if (ws) {
    ws.close()
    ws = null
  }
  if (clickFeedbackTimer) {
    clearTimeout(clickFeedbackTimer)
  }
})
</script>

<style scoped>
.remote-browser {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.status-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 14px;
}

.status-info {
  background: #e6f4ff;
  color: #1677ff;
}

.status-warning {
  background: #fff7e6;
  color: #fa8c16;
}

.status-success {
  background: #f6ffed;
  color: #52c41a;
}

.status-error {
  background: #fff2f0;
  color: #ff4d4f;
}

.browser-viewport {
  position: relative;
  width: 100%;
  aspect-ratio: 16 / 9;
  background: #1a1a1a;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
}

.screenshot {
  width: 100%;
  height: 100%;
  object-fit: contain;
  user-select: none;
  pointer-events: none;
}

.loading-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #888;
  gap: 16px;
}

.click-feedback {
  position: absolute;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: rgba(102, 126, 234, 0.5);
  transform: translate(-50%, -50%);
  pointer-events: none;
  animation: click-ripple 0.3s ease-out;
}

@keyframes click-ripple {
  0% {
    transform: translate(-50%, -50%) scale(0);
    opacity: 1;
  }
  100% {
    transform: translate(-50%, -50%) scale(2);
    opacity: 0;
  }
}

.keyboard-input {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.keyboard-hint {
  font-size: 12px;
  color: #888;
}

.actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 8px;
  border-top: 1px solid #eee;
}
</style>
