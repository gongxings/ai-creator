<template>
  <div class="playwright-viewer">
    <div class="viewer-header">
      <h3>{{ platform }} Playwright 授权</h3>
      <div v-if="targetAccount" class="auth-info">
        <el-tag type="success">账号: {{ targetAccount }}</el-tag>
        <el-tag v-if="authorizationComplete" type="success">授权完成</el-tag>
      </div>
      <div class="viewer-controls">
        <el-button-group>
          <el-button 
            :type="streaming ? 'danger' : 'primary'" 
            @click="toggleStreaming"
          >
            {{ streaming ? '停止流' : '开始流' }}
          </el-button>
          <el-button @click="captureScreenshot">截图</el-button>
          <el-button @click="refreshPage">刷新</el-button>
          <el-button type="danger" @click="disconnect">断开</el-button>
        </el-button-group>
      </div>
    </div>

    <div v-if="targetAccount && !authorizationComplete" class="auth-tips">
      <el-alert
        title="授权说明"
        type="success"
        :closable="false"
        show-icon
      >
        <p>1. 请在下方浏览器中登录 {{ platform }} 账号</p>
        <p>2. 登录成功后，系统会自动保存凭证</p>
        <p>3. 凭证保存后会自动返回设置页面</p>
      </el-alert>
    </div>

    <div class="viewer-content">
      <div class="screenshot-panel">
        <div class="screenshot-container">
          <img 
            v-if="screenshot" 
            :src="screenshotImageSrc" 
            alt="Browser screenshot" 
            class="screenshot-image"
          />
          <div v-else class="screenshot-placeholder">
            <el-icon size="48"><Picture /></el-icon>
            <p>等待截图...</p>
          </div>
        </div>
        
        <div class="url-bar">
          <el-input
            v-model="currentUrl"
            placeholder="输入URL并按回车导航"
            @keyup.enter="navigateToUrl"
            clearable
          >
            <template #prepend>URL</template>
            <template #append>
              <el-button @click="navigateToUrl">导航</el-button>
            </template>
          </el-input>
        </div>
      </div>

      <div class="log-panel">
        <div class="log-header">
          <span>操作日志</span>
          <el-button size="small" @click="clearLogs">清空</el-button>
        </div>
        <div class="log-content" ref="logContainer">
          <div 
            v-for="(log, index) in logs" 
            :key="index"
            :class="['log-item', 'log-' + log.level]"
          >
            <span class="log-time">{{ formatTime(log.timestamp) }}</span>
            <span :class="['log-level', 'level-' + log.level]">{{ log.level }}</span>
            <span class="log-message">{{ log.message }}</span>
          </div>
        </div>
      </div>
    </div>

    <div class="command-panel">
      <h4>执行命令</h4>
      <div class="command-form">
        <el-row :gutter="10">
          <el-col :span="8">
            <el-select v-model="commandType" placeholder="选择命令">
              <el-option label="点击元素" value="click" />
              <el-option label="输入文本" value="input" />
              <el-option label="执行脚本" value="execute" />
              <el-option label="等待" value="wait" />
            </el-select>
          </el-col>
          <el-col :span="12">
            <el-input 
              v-model="commandParam" 
              :placeholder="commandPlaceholder"
            />
          </el-col>
          <el-col :span="4">
            <el-button type="primary" @click="executeCommand" :disabled="!connected">
              执行
            </el-button>
          </el-col>
        </el-row>
      </div>
      
      <div v-if="commandType === 'input'" class="input-form" style="margin-top: 10px;">
        <el-row :gutter="10">
          <el-col :span="8">
            <span>选择器:</span>
          </el-col>
          <el-col :span="16">
            <el-input v-model="inputSelector" placeholder="元素选择器" />
          </el-col>
        </el-row>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { Picture } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const platformVal = route.params.platform as string || 'doubao'
const userIdVal = userStore.user?.id || 1
const tokenVal = userStore.token || ''

const platform = computed(() => platformVal)
const userId = computed(() => userIdVal)
const token = computed(() => tokenVal)

const targetAccount = computed(() => route.query.account as string || '')
const returnUrl = computed(() => route.query.return as string || '/settings')
const authorizationStarted = ref(false)

const authorizationComplete = ref(false)

const emit = defineEmits(['disconnect'])

const connected = ref(false)
const streaming = ref(false)
const screenshot = ref('')
const currentUrl = ref('')
const logs = ref<Array<{
  timestamp: string
  level: string
  message: string
  data?: any
}>>([])
const logContainer = ref<HTMLElement>()
const commandType = ref('click')
const commandParam = ref('')
const inputSelector = ref('')
const ws = ref<WebSocket | null>(null)

const screenshotImageSrc = computed(() => {
  if (screenshot.value) {
    return 'data:image/png;base64,' + screenshot.value
  }
  return ''
})

const commandPlaceholder = computed(() => {
  switch (commandType.value) {
    case 'click':
      return '元素选择器 (如 #login-btn)'
    case 'input':
      return '要输入的文本'
    case 'execute':
      return 'JavaScript 代码'
    case 'wait':
      return '等待时间(毫秒), 默认3000'
    default:
      return '命令参数'
  }
})

function formatTime(timestamp: string): string {
  try {
    const date = new Date(timestamp)
    return date.toLocaleTimeString()
  } catch {
    return timestamp
  }
}

function connectWebSocket() {
  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || '/api'
  const wsUrl = apiBaseUrl.replace('http', 'ws') + '/v1/ws/playwright/' + platform.value + '?user_id=' + userId.value
  ws.value = new WebSocket(wsUrl)
  
  ws.value.onopen = () => {
    connected.value = true
    addLog('info', 'WebSocket连接已建立')
    captureScreenshot()
    startStreaming()
    startAuthorization()
  }
  
  ws.value.onclose = () => {
    connected.value = false
    addLog('warning', 'WebSocket连接已关闭')
    authorizationStarted.value = false
  }
  
  ws.value.onerror = (error: Event) => {
    console.error('WebSocket错误:', error)
    addLog('error', 'WebSocket连接错误')
  }
  
  ws.value.onmessage = (event: MessageEvent) => {
    try {
      const data = JSON.parse(event.data)
      handleMessage(data)
    } catch (e) {
      console.error('消息解析失败:', e)
    }
  }
}

function handleMessage(data: any) {
  switch (data.type) {
    case 'log':
      addLog(data.level, data.message, data.data)
      break
    case 'screenshot':
      screenshot.value = data.image
      currentUrl.value = data.url || currentUrl.value
      break
    case 'url':
      currentUrl.value = data.url
      break
    case 'script_result':
      addLog('info', '脚本结果: ' + JSON.stringify(data.result))
      break
    case 'credentials_saved':
      authorizationComplete.value = true
      addLog('success', '授权完成！账号: ' + (data.account_name || targetAccount.value))
      ElMessage.success('授权成功！正在返回...')
      setTimeout(() => {
        router.push(returnUrl.value)
      }, 3000)
      break
    case 'error':
      addLog('error', data.message)
      break
  }
}

function addLog(level: string, message: string, data?: any) {
  logs.value.push({
    timestamp: new Date().toISOString(),
    level,
    message,
    data
  })
  
  if (logs.value.length > 500) {
    logs.value = logs.value.slice(-300)
  }
  
  nextTick(() => {
    if (logContainer.value) {
      logContainer.value.scrollTop = logContainer.value.scrollHeight
    }
  })
}

function clearLogs() {
  logs.value = []
}

function sendCommand(command: string, params: any = {}) {
  if (!ws.value || ws.value.readyState !== WebSocket.OPEN) {
    ElMessage.error('WebSocket未连接')
    return false
  }
  
  ws.value.send(JSON.stringify({ command, params }))
  return true
}

function captureScreenshot() {
  sendCommand('screenshot')
}

function refreshPage() {
  if (currentUrl.value) {
    navigateToUrl()
  } else {
    captureScreenshot()
  }
}

function navigateToUrl() {
  if (currentUrl.value) {
    let url = currentUrl.value
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
      url = 'https://' + url
    }
    sendCommand('navigate', { url })
  }
}

function toggleStreaming() {
  if (!connected.value) {
    ElMessage.error('WebSocket未连接，请刷新页面')
    return
  }

  if (streaming.value) {
    sendCommand('stop_streaming')
    streaming.value = false
    addLog('info', '已停止截图流')
  } else {
    const interval = 2000
    sendCommand('start_streaming', { interval })
    streaming.value = true
    addLog('info', '开始截图流，间隔: ' + interval + 'ms')
  }
}

function startStreaming() {
  if (streaming.value) {
    return
  }
  const interval = 2000
  sendCommand('start_streaming', { interval })
  streaming.value = true
  addLog('info', '开始截图流，间隔: ' + interval + 'ms')
}

function startAuthorization() {
  if (!connected.value || authorizationStarted.value) {
    return
  }
  const accountName = targetAccount.value || platform.value
  if (!accountName) {
    return
  }
  sendCommand('start_auth', { account_name: accountName })
  authorizationStarted.value = true
  addLog('info', `开始 Browser 授权: ${accountName}`)
}

function executeCommand() {
  switch (commandType.value) {
    case 'click':
      if (commandParam.value) {
        sendCommand('click', { selector: commandParam.value })
      }
      break
    case 'input':
      if (inputSelector.value && commandParam.value) {
        sendCommand('input', { 
          selector: inputSelector.value, 
          text: commandParam.value 
        })
      } else {
        ElMessage.warning('请输入选择器和文本')
      }
      break
    case 'execute':
      if (commandParam.value) {
        sendCommand('execute', { script: commandParam.value })
      }
      break
    case 'wait':
      const timeout = parseInt(commandParam.value) || 3000
      sendCommand('wait', { timeout })
      break
  }
}

function disconnect() {
  if (ws.value) {
    ws.value.close()
    ws.value = null
  }
  connected.value = false
  streaming.value = false
  emit('disconnect')
  authorizationStarted.value = false
}

onMounted(() => {
  if (!token.value) {
    addLog('error', '未登录，请先登录')
    ElMessage.error('请先登录')
    return
  }
  connectWebSocket()
})

onUnmounted(() => {
  if (streaming.value) {
    sendCommand('stop_streaming')
  }
  if (ws.value) {
    ws.value.close()
  }
})
</script>

<style scoped>
.playwright-viewer {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #1a1a2e;
  border-radius: 8px;
  overflow: hidden;
}

.viewer-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  border-bottom: 1px solid #0f3460;
}

.viewer-header h3 {
  margin: 0;
  color: #e8e8e8;
  font-size: 18px;
}

.auth-info {
  display: flex;
  gap: 8px;
}

.auth-tips {
  padding: 12px 16px;
  background: #16213e;
  border-bottom: 1px solid #0f3460;
}

.auth-tips .el-alert {
  background: transparent;
}

.viewer-controls {
  display: flex;
  gap: 8px;
}

.viewer-content {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.screenshot-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  border-right: 1px solid #0f3460;
}

.screenshot-container {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #0f0f23;
  min-height: 300px;
}

.screenshot-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.screenshot-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  color: #666;
}

.url-bar {
  padding: 10px;
  background: #16213e;
}

.log-panel {
  width: 320px;
  display: flex;
  flex-direction: column;
  background: #0f0f23;
}

.log-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  background: #16213e;
  border-bottom: 1px solid #0f3460;
  color: #e8e8e8;
  font-size: 14px;
}

.log-content {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.log-item {
  display: flex;
  align-items: flex-start;
  padding: 4px 0;
  font-size: 12px;
  border-bottom: 1px solid #1a1a2e;
}

.log-time {
  color: #666;
  min-width: 70px;
  font-family: monospace;
}

.log-level {
  min-width: 50px;
  font-weight: bold;
  text-transform: uppercase;
}

.level-info { color: #409eff; }
.level-warning { color: #e6a23c; }
.level-error { color: #f56c6c; }
.level-debug { color: #909399; }
.level-success { color: #67c23a; }

.log-message {
  color: #e8e8e8;
  word-break: break-all;
}

.command-panel {
  padding: 12px 16px;
  background: #16213e;
  border-top: 1px solid #0f3460;
}

.command-panel h4 {
  margin: 0 0 10px;
  color: #e8e8e8;
  font-size: 14px;
}

.command-form {
  margin-bottom: 10px;
}
</style>
