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
      <div class="login-card">
        <div class="login-shell">
          <section class="brand-panel">
            <div class="brand-header">
              <div class="brand-icon">✨</div>
              <h2>AI创作者平台</h2>
              <p class="brand-slogan">让创作更简单，让灵感更自由</p>
            </div>
            <div class="brand-body">
              <div class="brand-tags">
                <span class="tag">文案</span>
                <span class="tag">图片</span>
                <span class="tag">视频</span>
                <span class="tag">发布</span>
              </div>
              <ul class="brand-features">
                <li>
                  <span class="feature-icon">⚡</span>
                  <span>一键生成高质量初稿与标题</span>
                </li>
                <li>
                  <span class="feature-icon">🎯</span>
                  <span>模板与素材库，快速开始创作</span>
                </li>
                <li>
                  <span class="feature-icon">🚀</span>
                  <span>多平台同步发布与数据回看</span>
                </li>
              </ul>
              <div class="brand-note">
                <span class="note-dot"></span>
                聚焦效率与审美，让创作流程更顺滑
              </div>
            </div>
          </section>

          <section class="form-panel">
            <div class="form-header">
              <h3>欢迎回来</h3>
              <p>登录后继续你的创作</p>
            </div>

            <div class="form-container">
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
                    {{ loading ? '登录中...' : '立即登录' }}
                  </el-button>
                </el-form-item>

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

            <!-- 底部授权登录区域 -->
            <div class="auth-footer">
              <div class="divider">
                <span>第三方账号登录</span>
              </div>

              <div class="social-login">
                <el-button plain class="social-btn" title="微信登录">
                  <svg viewBox="0 0 1024 1024" width="20" height="20" fill="currentColor">
                    <path d="M664.250054 368.541681c10.015098 0 19.892049.732687 29.67281 1.795902-26.647917-122.810047-159.358451-214.077703-310.826188-214.077703-169.353083 0-308.085774 114.232694-308.085774 259.274068 0 83.708494 46.165436 152.460344 123.281791 205.78483l-30.80868 91.730191 107.688651-53.455469c38.558178 7.53665 69.459978 15.308661 107.924012 15.308661 9.66308 0 19.230993-.470721 28.752858-1.225921-6.025227-20.36584-9.521864-41.723264-9.521864-63.862493C402.285966 476.632491 517.47781 368.541681 664.250054 368.541681zM498.62897 285.87389c23.200398 0 38.557154 15.120372 38.557154 38.061874 0 22.846334-15.356756 38.156018-38.557154 38.156018-23.107277 0-46.260603-15.309684-46.260603-38.156018C452.368366 300.994262 475.522716 285.87389 498.62897 285.87389zM283.016307 362.090758c-23.107277 0-46.402843-15.309684-46.402843-38.156018 0-22.941502 23.295566-38.061874 46.402843-38.061874 23.081695 0 38.46301 15.120372 38.46301 38.061874C321.479317 346.782098 306.098002 362.090758 283.016307 362.090758zM945.448458 606.151333c0-121.888048-123.258254-221.236753-261.683954-221.236753-146.772244 0-262.251053 99.348706-262.251053 221.236753 0 122.06508 115.477786 221.200938 262.251053 221.200938 30.66644 0 61.617359-7.609305 92.423993-15.262612l84.513836 45.786813-23.178909-76.17082C899.379213 735.776599 945.448458 674.90216 945.448458 606.151333zM598.803483 567.994292c-15.332197 0-30.807656-15.096836-30.807656-30.501688 0-15.190981 15.47546-30.477129 30.807656-30.477129 23.295566 0 38.558178 15.286148 38.558178 30.477129C637.361661 552.897456 622.099049 567.994292 598.803483 567.994292zM768.25071 567.994292c-15.213493 0-30.594518-15.096836-30.594518-30.501688 0-15.190981 15.381024-30.477129 30.594518-30.477129 23.107277 0 38.558178 15.286148 38.558178 30.477129C806.808888 552.897456 791.357987 567.994292 768.25071 567.994292z"/>
                  </svg>
                </el-button>
                <el-button plain class="social-btn" title="QQ登录">
                  <svg viewBox="0 0 1024 1024" width="20" height="20" fill="currentColor">
                    <path d="M512 0C229.232 0 0 229.232 0 512s229.232 512 512 512 512-229.232 512-512S794.768 0 512 0z m297.28 643.52c-10.064 31.088-34.8 73.68-50.256 94.8 3.28 26.384-4.624 66.288-31.28 75.472-22.928 7.904-50.8-8.016-62.448-28.944-10.832 2.32-22.576 4.24-36.048 5.488 0 0-8.56 52.368-96.624 52.704h-5.248c-88.064-0.336-96.624-52.704-96.624-52.704-13.488-1.248-25.2-3.168-36.048-5.488-11.648 20.928-39.504 36.848-62.448 28.944-26.64-9.184-34.56-49.088-31.28-75.472-15.44-21.12-40.192-63.712-50.256-94.8-14.064-43.52 2.512-73.472 23.056-73.472 10.832 0 22.816 7.008 34.8 19.024 0.224-31.968 4.336-62.592 11.648-90.608-37.456-26.432-62.256-68.528-62.256-116.464 0-78.816 64.368-142.72 143.76-142.72 79.376 0 143.76 63.904 143.76 142.72 0 47.936-24.784 90.032-62.256 116.464 7.312 28.032 11.424 58.64 11.648 90.608 12-12.016 23.968-19.024 34.8-19.024 20.544 0 37.104 29.952 23.04 73.472z"/>
                  </svg>
                </el-button>
                <el-button plain class="social-btn" title="GitHub登录">
                  <svg viewBox="0 0 1024 1024" width="20" height="20" fill="currentColor">
                    <path d="M512 42.666667A464.64 464.64 0 0 0 42.666667 502.186667 460.373333 460.373333 0 0 0 363.52 938.666667c23.466667 4.266667 32-9.813333 32-22.186667v-78.08c-130.56 27.733333-158.293333-61.44-158.293333-61.44a122.026667 122.026667 0 0 0-52.053334-67.413333c-42.666667-28.16 3.413333-27.733333 3.413334-27.733334a98.56 98.56 0 0 1 71.68 47.36 101.12 101.12 0 0 0 136.533333 37.973334 99.413333 99.413333 0 0 1 29.866667-61.44c-104.106667-11.52-213.333333-50.773333-213.333334-226.986667a177.066667 177.066667 0 0 1 47.36-124.16 161.28 161.28 0 0 1 4.693334-121.173333s39.68-12.373333 128 46.933333a455.68 455.68 0 0 1 234.666666 0c89.6-59.306667 128-46.933333 128-46.933333a161.28 161.28 0 0 1 4.693334 121.173333A177.066667 177.066667 0 0 1 810.666667 477.866667c0 176.64-110.08 215.466667-213.333334 226.986666a106.666667 106.666667 0 0 1 32 85.333334v125.866666c0 14.933333 8.533333 26.88 32 22.186667A460.8 460.8 0 0 0 981.333333 502.186667 464.64 464.64 0 0 0 512 42.666667"/>
                  </svg>
                </el-button>
              </div>
            </div>
          </section>
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
import { User, Lock } from '@element-plus/icons-vue'
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
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&display=swap');

// 颜色变量 - 科技蓝配色
$primary-color: #2563eb;
$secondary-color: #38bdf8;
$accent-color: #0ea5e9;
$text-primary: #0f172a;
$text-secondary: #5b6472;
$bg-light: #f5f7ff;
$border-color: rgba(37, 99, 235, 0.18);
$shadow-sm: 0 6px 16px rgba(15, 23, 42, 0.08);
$shadow-md: 0 16px 32px rgba(15, 23, 42, 0.12);
$shadow-lg: 0 32px 60px rgba(15, 23, 42, 0.16);

.login-container {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  font-family: 'Outfit', 'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  color: $text-primary;
  background:
    radial-gradient(1200px circle at -10% -20%, rgba(56, 189, 248, 0.28) 0%, transparent 60%),
    radial-gradient(900px circle at 110% 0%, rgba(37, 99, 235, 0.24) 0%, transparent 55%),
    radial-gradient(800px circle at 50% 120%, rgba(14, 165, 233, 0.22) 0%, transparent 60%),
    linear-gradient(135deg, #f6f8ff 0%, #eef6ff 45%, #f3fbff 100%);
  overflow: hidden;

    &::before {
      content: '';
      position: absolute;
      inset: 0;
      background-image:
        linear-gradient(120deg, rgba(37, 99, 235, 0.1) 0%, transparent 40%),
        linear-gradient(to right, rgba(37, 99, 235, 0.05) 1px, transparent 1px),
        linear-gradient(to bottom, rgba(37, 99, 235, 0.05) 1px, transparent 1px);
      background-size: auto, 48px 48px, 48px 48px;
      opacity: 0.35;
      pointer-events: none;
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
  filter: blur(70px);
  opacity: 0.35;
  border-radius: 50%;

  &.blob-1 {
    width: 340px;
    height: 340px;
    background: rgba(56, 189, 248, 0.35);
    top: -120px;
    left: -120px;
    animation: float 8s ease-in-out infinite;
  }

  &.blob-2 {
    width: 280px;
    height: 280px;
    background: rgba(37, 99, 235, 0.3);
    bottom: -80px;
    right: -80px;
    animation: float 10s ease-in-out infinite reverse;
  }

  &.blob-3 {
    width: 220px;
    height: 220px;
    background: rgba(14, 165, 233, 0.25);
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
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  padding: 48px 24px;
  position: relative;
  z-index: 1;

  @media (max-width: 768px) {
    padding: 20px;
  }
}

// 统一的登录卡片
.login-card {
  position: relative;
  background: rgba(255, 255, 255, 0.82);
  border-radius: 26px;
  border: 1px solid rgba(255, 255, 255, 0.6);
  box-shadow: $shadow-lg;
  backdrop-filter: blur(18px) saturate(1.08);
  width: 100%;
  max-width: 1120px;
  overflow: hidden;
  animation: fadeInUp 0.7s cubic-bezier(0.16, 1, 0.3, 1);

  &::after {
    content: '';
    position: absolute;
    top: -45%;
    right: -35%;
    width: 300px;
    height: 300px;
    background: radial-gradient(circle, rgba(56, 189, 248, 0.2) 0%, transparent 70%);
    transform: rotate(20deg);
    pointer-events: none;
  }

  @media (max-width: 1024px) {
    max-width: 940px;
  }

  @media (max-width: 900px) {
    max-width: 720px;
  }

  @media (max-width: 768px) {
    max-width: 100%;
    border-radius: 20px;
  }
}

.login-shell {
  display: grid;
  grid-template-columns: 1.08fr 1fr;
  min-height: 560px;

  @media (max-width: 900px) {
    grid-template-columns: 1fr;
    min-height: auto;
  }
}

.brand-panel {
  padding: 44px 40px;
  background:
    linear-gradient(145deg, rgba(37, 99, 235, 0.18), rgba(56, 189, 248, 0.12)),
    radial-gradient(180px circle at 20% 15%, rgba(37, 99, 235, 0.2), transparent 70%);
  position: relative;

  &::after {
    content: '';
    position: absolute;
    top: 40px;
    right: 32px;
    width: 140px;
    height: 140px;
    border-radius: 28px;
    background: linear-gradient(135deg, rgba(37, 99, 235, 0.2), rgba(56, 189, 248, 0.22));
    filter: blur(8px);
    opacity: 0.7;
    pointer-events: none;
  }

  @media (max-width: 900px) {
    padding: 36px 32px;
  }

  @media (max-width: 600px) {
    padding: 32px 24px;
  }
}

.form-panel {
  padding: 44px 42px;
  background: rgba(255, 255, 255, 0.9);
  border-left: 1px solid rgba(37, 99, 235, 0.12);

  @media (max-width: 900px) {
    border-left: none;
    border-top: 1px solid rgba(37, 99, 235, 0.12);
    padding: 36px 32px 40px;
  }

  @media (max-width: 600px) {
    padding: 32px 24px;
  }
}

// 品牌头部 (约20%高度)
.brand-header {
  text-align: left;
  margin-bottom: 24px;
  padding-bottom: 18px;
  border-bottom: 1px solid rgba(37, 99, 235, 0.18);

  .brand-icon {
    width: 56px;
    height: 56px;
    font-size: 28px;
    margin: 0 0 12px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, rgba(37, 99, 235, 0.2), rgba(56, 189, 248, 0.26));
    border-radius: 16px;
    box-shadow: 0 12px 24px rgba(37, 99, 235, 0.24);
    transition: all 0.35s ease;

    &:hover {
      transform: scale(1.08) rotate(8deg);
    }
  }

  h2 {
    font-size: 26px;
    font-weight: 700;
    margin: 0 0 8px 0;
    letter-spacing: 0.4px;
    background: linear-gradient(135deg, $primary-color, $secondary-color 70%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  .brand-slogan {
    font-size: 13.5px;
    color: $text-secondary;
    margin: 0;
    letter-spacing: 0.4px;
  }
}

@media (max-width: 900px) {
  .brand-header {
    text-align: center;

    .brand-icon {
      margin: 0 auto 12px;
    }
  }

  .brand-tags {
    justify-content: center;
  }
}

.brand-body {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.brand-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;

  .tag {
    padding: 6px 12px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 600;
    color: $primary-color;
    background: rgba(255, 255, 255, 0.75);
    border: 1px solid rgba(37, 99, 235, 0.18);
    box-shadow: 0 6px 12px rgba(37, 99, 235, 0.1);
  }
}

.brand-features {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 14px;

  li {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    font-size: 14px;
    color: $text-primary;
    line-height: 1.5;
  }
}

.feature-icon {
  width: 28px;
  height: 28px;
  border-radius: 10px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.85);
  color: $primary-color;
  box-shadow: 0 6px 12px rgba(37, 99, 235, 0.12);
  flex-shrink: 0;
}

.brand-note {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
  color: $text-secondary;
  padding: 10px 14px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.7);
  border: 1px solid rgba(37, 99, 235, 0.12);
}

.note-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: linear-gradient(135deg, $primary-color, $secondary-color);
  box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.16);
}

.form-header {
  margin-bottom: 20px;

  h3 {
    margin: 0 0 6px 0;
    font-size: 22px;
    font-weight: 700;
    color: $text-primary;
  }

  p {
    margin: 0;
    font-size: 13.5px;
    color: $text-secondary;
  }
}

// 表单容器 (约60%高度)
.form-container {
  margin-bottom: 20px;
}

.login-form {
  .el-form-item {
    margin-bottom: 18px;

    &:last-child {
      margin-bottom: 0;
    }

    :deep(.el-input__wrapper) {
      border-radius: 12px;
      background: rgba(255, 255, 255, 0.86);
      border: 1px solid rgba(37, 99, 235, 0.14);
      box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.4),
        0 8px 16px rgba(37, 99, 235, 0.08);
      transition: all 0.3s ease;

      &:hover {
        border-color: rgba(37, 99, 235, 0.4);
        background: #ffffff;
      }

      &.is-focus {
        border-color: rgba(37, 99, 235, 0.6);
        box-shadow: 0 0 0 4px rgba(56, 189, 248, 0.22);
        background: #ffffff;
      }
    }

    :deep(.el-input__inner) {
      font-weight: 500;
      color: $text-primary;
    }

    :deep(.el-input__inner::placeholder) {
      color: rgba(91, 100, 114, 0.75);
    }

    :deep(.el-input__prefix) {
      color: rgba(37, 99, 235, 0.75);
    }
  }

  // 记住我和忘记密码
  .remember-forgot-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin: 18px 0 8px;
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
      color: $primary-color;
      text-decoration: underline;
    }
  }

  // 登录按钮
  .login-button {
    width: 100%;
    height: 46px;
    font-size: 16px;
    font-weight: 600;
    border-radius: 12px;
    background: linear-gradient(135deg, $primary-color 0%, $accent-color 45%, $secondary-color 100%);
    border: none;
    color: white;
    transition: all 0.3s ease;
    margin: 18px 0 16px 0;
    position: relative;
    overflow: hidden;

    &::after {
      content: '';
      position: absolute;
      inset: 2px;
      border-radius: 10px;
      background: linear-gradient(135deg, rgba(255, 255, 255, 0.28), transparent 60%);
      opacity: 0;
      transition: opacity 0.3s ease;
      pointer-events: none;
    }

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 14px 28px rgba(37, 99, 235, 0.35);

      &::after {
        opacity: 1;
      }
    }

    &:active {
      transform: translateY(0);
    }
  }

  // 注册链接
  .register-section {
    text-align: center;
    font-size: 14px;
    color: $text-secondary;

    span {
      margin-right: 4px;
    }

    .register-link {
      font-weight: 600;
      transition: all 0.3s ease;

      &:hover {
        color: $primary-color;
      }
    }
  }
}

// 底部授权区域 (约20%高度)
.auth-footer {
  padding-top: 20px;
  border-top: 1px solid rgba(37, 99, 235, 0.12);

  // 分割线
  .divider {
    text-align: center;
    margin-bottom: 16px;
    color: $text-secondary;
    font-size: 12px;

    span {
      position: relative;
      padding: 0 12px;

      &::before,
      &::after {
        content: '';
        position: absolute;
        top: 50%;
        width: 48px;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(37, 99, 235, 0.4));
      }

      &::before {
        right: 100%;
      }

      &::after {
        left: 100%;
        transform: scaleX(-1);
      }
    }
  }

  // 社交登录
  .social-login {
    display: flex;
    gap: 12px;
    justify-content: center;

    .social-btn {
      width: 48px;
      height: 48px;
      padding: 0;
      border-radius: 14px;
      border: 1px solid rgba(37, 99, 235, 0.2);
      color: rgba(37, 99, 235, 0.85);
      background: rgba(255, 255, 255, 0.75);
      transition: all 0.3s ease;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 8px 14px rgba(37, 99, 235, 0.12);

      &:hover {
        border-color: rgba(37, 99, 235, 0.55);
        color: $primary-color;
        background: linear-gradient(135deg, rgba(37, 99, 235, 0.12), rgba(56, 189, 248, 0.12));
        transform: translateY(-3px);
        box-shadow: 0 12px 20px rgba(37, 99, 235, 0.22);
      }

      svg {
        display: block;
      }
    }
  }
}

// 动画
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

// 暗模式支持
@media (prefers-color-scheme: dark) {
  .login-card {
    background: rgba(17, 24, 39, 0.85);
    color: #f8fafc;
  }

  .brand-panel {
    background:
      linear-gradient(145deg, rgba(37, 99, 235, 0.28), rgba(56, 189, 248, 0.18)),
      radial-gradient(180px circle at 20% 15%, rgba(56, 189, 248, 0.2), transparent 70%);
  }

  .form-panel {
    background: rgba(15, 23, 42, 0.8);
    border-left-color: rgba(255, 255, 255, 0.12);
    border-top-color: rgba(255, 255, 255, 0.12);
  }

  .brand-header {
    border-bottom-color: rgba(255, 255, 255, 0.12);
  }

  .auth-footer {
    border-top-color: rgba(255, 255, 255, 0.12);
  }

  .brand-tags .tag {
    background: rgba(15, 23, 42, 0.6);
    color: rgba(147, 197, 253, 0.9);
    border-color: rgba(147, 197, 253, 0.25);
  }

  .feature-icon,
  .brand-note {
    background: rgba(30, 41, 59, 0.8);
    color: rgba(147, 197, 253, 0.9);
    border-color: rgba(148, 163, 184, 0.2);
  }

  .login-form {
    :deep(.el-input__wrapper) {
      background: rgba(30, 41, 59, 0.6);
      border-color: rgba(255, 255, 255, 0.12);

      &:hover {
        background: rgba(30, 41, 59, 0.85);
      }
    }
  }

  .social-btn {
    background: rgba(30, 41, 59, 0.7);
    color: rgba(147, 197, 253, 0.85);
    border-color: rgba(147, 197, 253, 0.2);
  }
}

@media (max-width: 420px) {
  .login-card {
    border-radius: 18px;
  }

  .brand-header h2 {
    font-size: 22px;
  }

  .form-header h3 {
    font-size: 20px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .login-card,
  .gradient-blob {
    animation: none !important;
  }
}
</style>
