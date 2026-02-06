<template>
  <div class="login-container">
    <!-- 背景装饰 -->
    <div class="background-decoration">
      <div class="gradient-blob blob-1"></div>
      <div class="gradient-blob blob-2"></div>
      <div class="gradient-blob blob-3"></div>
    </div>

    <!-- 登录内容 -->
    <div class="login-content">
      <!-- 左侧品牌区域 -->
      <div class="brand-section">
        <div class="brand-card">
          <div class="brand-icon">
            <div class="icon-bg">✨</div>
          </div>
          <h2>AI创作者平台</h2>
          <p class="brand-slogan">让创作更简单，让灵感更自由</p>
          
          <div class="features">
            <div class="feature-item">
              <span class="feature-icon">📝</span>
              <span>14个专业写作工具</span>
            </div>
            <div class="feature-item">
              <span class="feature-icon">🎨</span>
              <span>AI图片视频生成</span>
            </div>
            <div class="feature-item">
              <span class="feature-icon">🚀</span>
              <span>一键多平台发布</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧登录表单 -->
      <div class="form-section">
        <div class="form-container">
          <div class="form-header">
            <h3>欢迎登录</h3>
            <p>使用账户访问您的创作空间</p>
          </div>

          <el-form
            ref="loginFormRef"
            :model="loginForm"
            :rules="loginRules"
            class="login-form"
            @submit.prevent="handleLogin"
          >
            <!-- 用户名/邮箱输入 -->
            <el-form-item prop="username">
              <el-input
                v-model="loginForm.username"
                placeholder="用户名或邮箱"
                size="large"
                :prefix-icon="User"
                clearable
                @keyup.enter="handleLogin"
              />
            </el-form-item>

            <!-- 密码输入 -->
            <el-form-item prop="password">
              <el-input
                v-model="loginForm.password"
                type="password"
                placeholder="密码"
                size="large"
                :prefix-icon="Lock"
                show-password
                clearable
                @keyup.enter="handleLogin"
              />
            </el-form-item>

            <!-- 记住我和忘记密码 - 分离布局 -->
            <div class="remember-forgot-row">
              <div class="remember-checkbox">
                <el-checkbox v-model="loginForm.remember">
                  <span>记住我</span>
                </el-checkbox>
              </div>
              <el-link 
                type="primary" 
                :underline="false" 
                class="forgot-password-link"
                @click="goToForgotPassword"
              >
                忘记密码？
              </el-link>
            </div>

            <!-- 登录按钮 -->
            <el-form-item>
              <el-button
                type="primary"
                size="large"
                :loading="loading"
                class="login-button"
                @click="handleLogin"
              >
                <template v-if="!loading">
                  <el-icon style="margin-right: 8px"><VideoPlay /></el-icon>
                  立即登录
                </template>
                <template v-else>
                  登录中...
                </template>
              </el-button>
            </el-form-item>

            <!-- 其他登录方式 -->
            <div class="divider">
              <span>或者</span>
            </div>

            <div class="social-login">
              <el-button plain class="social-btn" title="暂未开放">
                <svg viewBox="0 0 24 24" width="1em" height="1em" fill="currentColor">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8z"/>
                </svg>
              </el-button>
              <el-button plain class="social-btn" title="暂未开放">
                <svg viewBox="0 0 24 24" width="1em" height="1em" fill="currentColor">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8z"/>
                </svg>
              </el-button>
              <el-button plain class="social-btn" title="暂未开放">
                <svg viewBox="0 0 24 24" width="1em" height="1em" fill="currentColor">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8z"/>
                </svg>
              </el-button>
            </div>

            <!-- 注册链接 -->
            <div class="register-section">
              <span>还没有账号？</span>
              <el-link 
                type="primary" 
                :underline="false" 
                class="register-link"
                @click="goToRegister"
              >
                立即注册
              </el-link>
            </div>
          </el-form>
        </div>
      </div>
    </div>

    <!-- 忘记密码弹窗 -->
    <el-dialog 
      v-model="showForgotDialog"
      title="重置密码"
      width="400px"
      :close-on-click-modal="false"
    >
      <p style="margin-bottom: 16px; color: #666;">
        请输入您的邮箱地址，我们将发送重置密码链接到您的邮箱。
      </p>
      <el-input
        v-model="resetEmail"
        placeholder="请输入您的邮箱"
        clearable
      />
      <template #footer>
        <el-button @click="showForgotDialog = false">取消</el-button>
        <el-button type="primary" @click="handleReset" :loading="resetLoading">
          发送重置链接
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { User, Lock, VideoPlay } from '@element-plus/icons-vue'
import { useUserStore } from '@/store/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const loginFormRef = ref<FormInstance>()
const loading = ref(false)
const showForgotDialog = ref(false)
const resetEmail = ref('')
const resetLoading = ref(false)

const loginForm = reactive({
  username: '',
  password: '',
  remember: false,
})

const loginRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名或邮箱', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' },
  ],
}

const handleLogin = async () => {
  if (!loginFormRef.value) return

  await loginFormRef.value.validate(async (valid) => {
    if (!valid) return

    loading.value = true
    try {
      await userStore.login(loginForm.username, loginForm.password)

      ElMessage.success('登录成功')

      // 跳转到之前的页面或首页
      const redirect = (route.query.redirect as string) || '/'
      router.push(redirect)
    } catch (error: any) {
      ElMessage.error(error.message || '登录失败，请检查用户名和密码')
    } finally {
      loading.value = false
    }
  })
}

const goToRegister = () => {
  router.push('/register')
}

const goToForgotPassword = () => {
  showForgotDialog.value = true
  resetEmail.value = ''
}

const handleReset = async () => {
  if (!resetEmail.value) {
    ElMessage.warning('请输入您的邮箱地址')
    return
  }

  resetLoading.value = true
  try {
    // TODO: 调用重置密码 API
    ElMessage.success('重置链接已发送到您的邮箱，请检查收件箱')
    showForgotDialog.value = false
    resetEmail.value = ''
  } catch (error: any) {
    ElMessage.error(error.message || '发送失败，请稍后重试')
  } finally {
    resetLoading.value = false
  }
}
</script>

<style scoped lang="scss">
// 颜色变量
$primary-color: #667eea;
$secondary-color: #764ba2;
$accent-color: #f093fb;
$danger-color: #ff6b6b;
$text-primary: #2d3436;
$text-secondary: #636e72;
$bg-light: #f8f9fa;
$border-color: #e9ecef;
$shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.08);
$shadow-md: 0 8px 16px rgba(0, 0, 0, 0.12);
$shadow-lg: 0 12px 32px rgba(0, 0, 0, 0.15);

.login-container {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
  overflow: hidden;

  // 响应式字体大小
  @media (max-width: 1200px) {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  }
}

// 背景装饰
.background-decoration {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  z-index: 0;
}

.gradient-blob {
  position: absolute;
  filter: blur(60px);
  opacity: 0.3;
  border-radius: 50%;

  &.blob-1 {
    width: 300px;
    height: 300px;
    background: rgba(255, 255, 255, 0.4);
    top: -100px;
    left: -100px;
    animation: float 8s ease-in-out infinite;
  }

  &.blob-2 {
    width: 250px;
    height: 250px;
    background: rgba(240, 147, 251, 0.3);
    bottom: -50px;
    right: -50px;
    animation: float 10s ease-in-out infinite reverse;
  }

  &.blob-3 {
    width: 200px;
    height: 200px;
    background: rgba(102, 126, 234, 0.2);
    top: 50%;
    right: 10%;
    animation: float 12s ease-in-out infinite;
  }
}

@keyframes float {
  0%, 100% {
    transform: translate(0, 0);
  }
  33% {
    transform: translate(30px, -30px);
  }
  66% {
    transform: translate(-20px, 20px);
  }
}

// 登录内容
.login-content {
  display: flex;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
  gap: 60px;
  position: relative;
  z-index: 1;
  align-items: center;

  @media (max-width: 768px) {
    flex-direction: column;
    gap: 40px;
    padding: 20px;
    max-width: 100%;
  }
}

// 品牌区域
.brand-section {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 500px;

  @media (max-width: 768px) {
    min-height: auto;
    margin-top: 20px;
  }
}

.brand-card {
  background: rgba(255, 255, 255, 0.95);
  padding: 50px 40px;
  border-radius: 20px;
  text-align: center;
  backdrop-filter: blur(10px);
  box-shadow: $shadow-lg;
  max-width: 350px;
  animation: slideInLeft 0.8s ease-out;

  @media (max-width: 768px) {
    max-width: 100%;
    padding: 30px 20px;
  }
}

.brand-icon {
  margin-bottom: 24px;
  
  .icon-bg {
    width: 80px;
    height: 80px;
    background: linear-gradient(135deg, $primary-color, $secondary-color);
    border-radius: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 40px;
    margin: 0 auto;
    box-shadow: 0 8px 16px rgba(102, 126, 234, 0.3);
  }
}

.brand-card {
  h2 {
    font-size: 28px;
    font-weight: 700;
    color: $text-primary;
    margin-bottom: 8px;
    background: linear-gradient(135deg, $primary-color, $secondary-color);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  .brand-slogan {
    font-size: 14px;
    color: $text-secondary;
    margin-bottom: 32px;
    line-height: 1.6;
  }
}

.features {
  text-align: left;
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-top: 32px;
  padding-top: 32px;
  border-top: 1px solid $border-color;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
  color: $text-secondary;
  transition: all 0.3s ease;

  .feature-icon {
    font-size: 20px;
    display: flex;
    align-items: center;
  }

  &:hover {
    color: $primary-color;
    transform: translateX(5px);
  }
}

// 表单区域
.form-section {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 500px;

  @media (max-width: 768px) {
    min-height: auto;
    width: 100%;
  }
}

.form-container {
  background: rgba(255, 255, 255, 0.98);
  padding: 50px 40px;
  border-radius: 20px;
  box-shadow: $shadow-lg;
  width: 100%;
  max-width: 400px;
  backdrop-filter: blur(10px);
  animation: slideInRight 0.8s ease-out;

  @media (max-width: 768px) {
    max-width: 100%;
    padding: 30px 20px;
  }
}

.form-header {
  text-align: center;
  margin-bottom: 32px;

  h3 {
    font-size: 24px;
    font-weight: 700;
    color: $text-primary;
    margin-bottom: 8px;
  }

  p {
    font-size: 14px;
    color: $text-secondary;
  }
}

.login-form {
  .el-form-item {
    margin-bottom: 20px;

    &:last-child {
      margin-bottom: 0;
    }

    :deep(.el-input__wrapper) {
      border-radius: 10px;
      background: $bg-light;
      border: 1px solid $border-color;
      transition: all 0.3s ease;

      &:hover {
        border-color: $primary-color;
        background: #fff;
      }

      &.is-focus {
        border-color: $primary-color;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1);
        background: #fff;
      }
    }
  }

  // 记住我和忘记密码
  .remember-forgot-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin: 24px 0;
    gap: 12px;

    @media (max-width: 480px) {
      flex-direction: column;
      align-items: flex-start;
      gap: 12px;
    }
  }

  .remember-checkbox {
    :deep(.el-checkbox__label) {
      font-size: 14px;
      color: $text-secondary;
      user-select: none;
    }

    :deep(.el-checkbox) {
      &.is-checked .el-checkbox__inner {
        background-color: $primary-color;
        border-color: $primary-color;
      }
    }
  }

  .forgot-password-link {
    font-size: 14px;
    white-space: nowrap;
    transition: all 0.3s ease;

    &:hover {
      color: $secondary-color;
      text-decoration: underline;
    }
  }

  // 登录按钮
  .login-button {
    width: 100%;
    height: 44px;
    font-size: 16px;
    font-weight: 600;
    border-radius: 10px;
    background: linear-gradient(135deg, $primary-color, $secondary-color);
    border: none;
    color: white;
    transition: all 0.3s ease;
    margin: 24px 0;

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
    }

    &:active {
      transform: translateY(0);
    }

    :deep(.el-icon) {
      transition: transform 0.3s ease;
    }

    &:hover :deep(.el-icon) {
      transform: scale(1.1);
    }
  }

  // 分割线
  .divider {
    text-align: center;
    margin: 24px 0;
    position: relative;
    color: $text-secondary;
    font-size: 12px;

    &::before {
      content: '';
      position: absolute;
      left: 0;
      top: 50%;
      width: 35%;
      height: 1px;
      background: $border-color;
    }

    &::after {
      content: '';
      position: absolute;
      right: 0;
      top: 50%;
      width: 35%;
      height: 1px;
      background: $border-color;
    }

    span {
      position: relative;
      background: white;
      padding: 0 8px;
    }
  }

  // 社交登录
  .social-login {
    display: flex;
    gap: 12px;
    justify-content: center;
    margin-bottom: 24px;

    .social-btn {
      width: 44px;
      height: 44px;
      padding: 0;
      border-radius: 10px;
      border: 1px solid $border-color;
      color: $text-secondary;
      transition: all 0.3s ease;

      &:hover {
        border-color: $primary-color;
        color: $primary-color;
        background: rgba(102, 126, 234, 0.05);
        transform: translateY(-2px);
      }

      svg {
        display: block;
      }
    }
  }

  // 注册链接
  .register-section {
    text-align: center;
    font-size: 14px;
    color: $text-secondary;
    padding-top: 24px;
    border-top: 1px solid $border-color;

    span {
      margin-right: 4px;
    }

    .register-link {
      font-weight: 600;
      transition: all 0.3s ease;

      &:hover {
        color: $secondary-color;
      }
    }
  }
}

// 动画
@keyframes slideInLeft {
  from {
    opacity: 0;
    transform: translateX(-30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

// 暗模式支持
@media (prefers-color-scheme: dark) {
  .form-container,
  .brand-card {
    background: rgba(45, 52, 54, 0.95);
    color: #ecf0f1;
  }

  .login-form {
    :deep(.el-input__wrapper) {
      background: rgba(52, 73, 94, 0.5);
      border-color: rgba(255, 255, 255, 0.1);

      &:hover {
        background: rgba(52, 73, 94, 0.8);
      }
    }
  }
}

// 响应式设计
@media (max-width: 1024px) {
  .login-content {
    gap: 40px;
  }

  .brand-card,
  .form-container {
    padding: 40px 30px;
  }
}

@media (max-width: 768px) {
  .login-container {
    padding: 20px;
  }

  .login-content {
    flex-direction: column;
  }

  .form-container {
    max-width: 100%;
    width: 100%;
  }

  .brand-card {
    max-width: 100%;
    width: 100%;
  }
}
</style>

