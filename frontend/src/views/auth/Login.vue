<template>
  <div class="login-container">
    <div class="background-decoration">
      <div class="gradient-blob blob-1"></div>
      <div class="gradient-blob blob-2"></div>
      <div class="gradient-blob blob-3"></div>
    </div>

    <div class="login-content">
      <div class="login-card">
        <div class="login-shell">
          <section class="brand-panel">
            <div class="brand-header">
              <div class="brand-icon">AI</div>
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
                  <span class="feature-icon">1</span>
                  <span>一站式完成写作、图片、视频与发布流程</span>
                </li>
                <li>
                  <span class="feature-icon">2</span>
                  <span>模板、素材和工作流整合，开箱即可开始创作</span>
                </li>
                <li>
                  <span class="feature-icon">3</span>
                  <span>多平台发布与数据回看，保持内容生产连续性</span>
                </li>
              </ul>
              <div class="brand-note">
                <span class="note-dot"></span>
                聚焦效率与审美，让创作体验更顺滑
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

                <div class="remember-forgot-row">
                  <div class="remember-checkbox">
                    <el-checkbox v-model="loginForm.remember">
                      <span>记住我</span>
                    </el-checkbox>
                  </div>
                  <el-link type="primary" :underline="false" class="forgot-password-link" @click="goToForgotPassword">
                    忘记密码？
                  </el-link>
                </div>

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

                <div class="register-section">
                  <span>还没有账号？</span>
                  <el-link type="primary" :underline="false" class="register-link" @click="goToRegister">
                    立即注册
                  </el-link>
                </div>
              </el-form>
            </div>

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

    <el-dialog v-model="showForgotDialog" title="重置密码" width="400px" :close-on-click-modal="false">
      <p style="margin-bottom: 16px; color: #666;">
        请输入您的邮箱地址，我们将发送重置密码链接到您的邮箱。
      </p>
      <el-input v-model="resetEmail" placeholder="请输入您的邮箱" clearable />
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
import { requestPasswordReset } from '@/api/auth'

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
  username: [{ required: true, message: '请输入用户名或邮箱', trigger: 'blur' }],
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
    await requestPasswordReset({ email: resetEmail.value })
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
$primary-color: #2563eb;
$secondary-color: #38bdf8;
$accent-color: #0ea5e9;
$text-primary: #0f172a;
$text-secondary: #5b6472;
$shadow-lg: 0 32px 60px rgba(15, 23, 42, 0.16);

.login-container {
  position: relative;
  min-height: 100dvh;
  overflow: hidden;
  color: $text-primary;
  background:
    radial-gradient(1200px circle at -10% -20%, rgba(56, 189, 248, 0.28) 0%, transparent 60%),
    radial-gradient(900px circle at 110% 0%, rgba(37, 99, 235, 0.24) 0%, transparent 55%),
    radial-gradient(800px circle at 50% 120%, rgba(14, 165, 233, 0.2) 0%, transparent 60%),
    linear-gradient(135deg, #f6f8ff 0%, #eef6ff 45%, #f3fbff 100%);

  &::before {
    content: '';
    position: absolute;
    inset: 0;
    background-image:
      linear-gradient(120deg, rgba(37, 99, 235, 0.08) 0%, transparent 40%),
      linear-gradient(to right, rgba(37, 99, 235, 0.05) 1px, transparent 1px),
      linear-gradient(to bottom, rgba(37, 99, 235, 0.05) 1px, transparent 1px);
    background-size: auto, 48px 48px, 48px 48px;
    opacity: 0.35;
    pointer-events: none;
  }
}

.background-decoration {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 0;
}

.gradient-blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(70px);
  opacity: 0.35;

  &.blob-1 {
    width: 340px;
    height: 340px;
    top: -120px;
    left: -120px;
    background: rgba(56, 189, 248, 0.35);
    animation: float 8s ease-in-out infinite;
  }

  &.blob-2 {
    width: 280px;
    height: 280px;
    right: -80px;
    bottom: -80px;
    background: rgba(37, 99, 235, 0.3);
    animation: float 10s ease-in-out infinite reverse;
  }

  &.blob-3 {
    width: 220px;
    height: 220px;
    top: 50%;
    right: 10%;
    background: rgba(14, 165, 233, 0.25);
    animation: float 12s ease-in-out infinite;
  }
}

.login-content {
  position: relative;
  z-index: 1;
  min-height: 100dvh;
  padding: 24px 32px;
  display: flex;
  align-items: stretch;
  justify-content: center;
}

.login-card {
  position: relative;
  width: min(800px, 100%);
  min-height: calc(100dvh - 48px);
  overflow: hidden;
  border-radius: 26px;
  border: 1px solid rgba(255, 255, 255, 0.6);
  background: rgba(255, 255, 255, 0.82);
  box-shadow: $shadow-lg;
  backdrop-filter: blur(18px) saturate(1.08);
  animation: fadeInUp 0.7s cubic-bezier(0.16, 1, 0.3, 1);

  &::before {
    content: '';
    position: absolute;
    inset: 0 0 auto 0;
    height: 3px;
    background: linear-gradient(90deg, rgba(37, 99, 235, 0.1), rgba(37, 99, 235, 0.85), rgba(56, 189, 248, 0.8));
  }
}

.login-shell {
  display: grid;
  grid-template-columns: minmax(0, 1.05fr) minmax(0, 0.95fr);
  min-height: inherit;
}

.brand-panel {
  position: relative;
  padding: 44px 40px;
  display: flex;
  flex-direction: column;
  gap: 24px;
  background:
    linear-gradient(145deg, rgba(37, 99, 235, 0.18), rgba(56, 189, 248, 0.12)),
    radial-gradient(180px circle at 20% 15%, rgba(37, 99, 235, 0.2), transparent 70%);

  &::after {
    content: '';
    position: absolute;
    inset: 24px;
    border-radius: 24px;
    border: 1px solid rgba(255, 255, 255, 0.34);
    pointer-events: none;
  }
}

.form-panel {
  padding: 44px 42px;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.95), rgba(239, 246, 255, 0.92));
  border-left: 1px solid rgba(37, 99, 235, 0.12);
}

.brand-header {
  margin-bottom: 4px;

  .brand-icon {
    width: 60px;
    height: 60px;
    margin-bottom: 18px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border-radius: 18px;
    font-size: 18px;
    font-weight: 700;
    letter-spacing: 0.08em;
    background: linear-gradient(135deg, rgba(37, 99, 235, 0.2), rgba(56, 189, 248, 0.22));
    box-shadow: 0 12px 24px rgba(37, 99, 235, 0.18);
  }

  h2 {
    margin: 0 0 10px;
    font-size: 32px;
    font-weight: 700;
    line-height: 1.15;
    letter-spacing: -0.6px;
  }

  .brand-slogan {
    margin: 0;
    font-size: 15px;
    line-height: 1.6;
    color: $text-secondary;
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
  gap: 10px;

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
    line-height: 1.5;
  }
}

.feature-icon {
  width: 28px;
  height: 28px;
  flex-shrink: 0;
  border-radius: 10px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  background: rgba(255, 255, 255, 0.84);
  color: $primary-color;
  box-shadow: 0 6px 12px rgba(37, 99, 235, 0.12);
}

.brand-note {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 13px;
  color: $text-secondary;
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
    margin: 0 0 6px;
    font-size: 22px;
    font-weight: 700;
  }

  p {
    margin: 0;
    font-size: 13.5px;
    color: $text-secondary;
  }
}

.form-container {
  margin-bottom: 20px;
}

.login-form {
  width: 100%;

  :deep(.el-form-item__content),
  :deep(.el-input) {
    width: 100%;
  }

  .el-form-item {
    margin-bottom: 18px;

    &:last-child {
      margin-bottom: 0;
    }

    :deep(.el-input__wrapper) {
      border-radius: 12px;
      background: rgba(255, 255, 255, 0.86);
      border: 1px solid rgba(37, 99, 235, 0.14);
      box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.4), 0 8px 16px rgba(37, 99, 235, 0.08);
      transition: all 0.3s ease;

      &:hover {
        border-color: rgba(37, 99, 235, 0.4);
        background: #fff;
      }

      &.is-focus {
        border-color: rgba(37, 99, 235, 0.6);
        box-shadow: 0 0 0 4px rgba(56, 189, 248, 0.22);
        background: #fff;
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

  .remember-forgot-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
    margin: 18px 0 8px;
  }

  .remember-checkbox {
    :deep(.el-checkbox__label) {
      font-size: 14px;
      color: $text-secondary;
    }
  }

  .forgot-password-link {
    font-size: 14px;
    white-space: nowrap;
  }

  .login-button {
    width: 100%;
    height: 46px;
    margin: 18px 0 16px;
    border: none;
    border-radius: 12px;
    font-size: 16px;
    font-weight: 600;
    color: #fff;
    background: linear-gradient(135deg, $primary-color 0%, $accent-color 45%, $secondary-color 100%);
    box-shadow: 0 16px 28px rgba(37, 99, 235, 0.2);
  }

  .register-section {
    text-align: center;
    font-size: 14px;
    color: $text-secondary;

    span {
      margin-right: 4px;
    }

    .register-link {
      font-weight: 600;
    }
  }
}

.auth-footer {
  padding-top: 20px;
  border-top: 1px solid rgba(37, 99, 235, 0.12);

  .divider {
    margin-bottom: 16px;
    text-align: center;
    font-size: 12px;
    color: $text-secondary;

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

  .social-login {
    display: flex;
    justify-content: center;
    gap: 12px;
  }

  .social-btn {
    width: 48px;
    height: 48px;
    padding: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 14px;
    border: 1px solid rgba(37, 99, 235, 0.2);
    background: rgba(255, 255, 255, 0.75);
    color: rgba(37, 99, 235, 0.85);
    box-shadow: 0 8px 14px rgba(37, 99, 235, 0.12);
  }
}

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

@keyframes float {
  0%,
  100% {
    transform: translate(0, 0);
  }

  33% {
    transform: translate(30px, -30px);
  }

  66% {
    transform: translate(-20px, 20px);
  }
}

@media (max-width: 900px) {
  .login-content {
    padding: 20px;
  }

  .login-card {
    min-height: auto;
  }

  .login-shell {
    grid-template-columns: 1fr;
  }

  .form-panel {
    order: 1;
    padding: 34px 32px 26px;
    border-left: none;
  }

  .brand-panel {
    order: 2;
    padding: 30px 32px 32px;
  }

  .brand-header {
    margin-bottom: 0;
    text-align: center;

    .brand-icon {
      margin: 0 auto 10px;
    }

    h2 {
      font-size: 24px;
      margin-bottom: 6px;
    }
  }

  .brand-body {
    margin-top: 18px;
  }

  .brand-tags {
    justify-content: center;
  }
}

@media (max-width: 600px) {
  .background-decoration {
    opacity: 0.55;
  }

  .gradient-blob {
    filter: blur(60px);

    &.blob-1 {
      width: 220px;
      height: 220px;
      top: -80px;
      left: -90px;
    }

    &.blob-2 {
      width: 180px;
      height: 180px;
      right: -50px;
      bottom: -40px;
    }

    &.blob-3 {
      display: none;
    }
  }

  .login-content {
    min-height: auto;
    padding: 12px;
    display: block;
  }

  .login-card {
    min-height: auto;
    border-radius: 18px;
  }

  .form-panel {
    padding: 22px 20px 18px;
  }

  .brand-panel {
    padding: 20px;
    background:
      linear-gradient(145deg, rgba(37, 99, 235, 0.14), rgba(56, 189, 248, 0.08)),
      radial-gradient(160px circle at 20% 10%, rgba(37, 99, 235, 0.14), transparent 70%);
  }

  .brand-header {
    text-align: left;
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;

    .brand-icon {
      width: 48px;
      height: 48px;
      margin: 0 0 6px;
      font-size: 16px;
    }

    h2 {
      font-size: 22px;
      line-height: 1.2;
    }

    .brand-slogan {
      font-size: 13px;
    }
  }

  .brand-body {
    gap: 14px;
    margin-top: 14px;
  }

  .brand-tags {
    gap: 8px;
    justify-content: flex-start;
  }

  .brand-features {
    gap: 10px;

    li {
      font-size: 13px;
    }
  }

  .feature-icon {
    width: 24px;
    height: 24px;
    border-radius: 8px;
    font-size: 11px;
  }

  .brand-note {
    padding: 8px 10px;
    font-size: 12px;
  }

  .form-header {
    margin-bottom: 16px;

    h3 {
      font-size: 20px;
    }
  }

  .form-container {
    margin-bottom: 16px;
  }

  .login-form {
    .el-form-item {
      margin-bottom: 14px;
    }

    .remember-forgot-row {
      margin-top: 12px;
    }

    .login-button {
      height: 44px;
      margin: 14px 0;
    }
  }

  .auth-footer {
    padding-top: 16px;

    .divider span {
      &::before,
      &::after {
        width: 32px;
      }
    }

    .social-login {
      gap: 10px;
    }

    .social-btn {
      width: 44px;
      height: 44px;
      border-radius: 12px;
    }
  }
}

@media (max-width: 420px) {
  .login-content {
    padding: 10px;
  }

  .login-card {
    border-radius: 16px;
  }

  .brand-header h2 {
    font-size: 20px;
  }

  .form-header h3 {
    font-size: 18px;
  }

  .brand-body {
    gap: 12px;
  }

  .login-form {
    .remember-forgot-row {
      flex-direction: column;
      align-items: stretch;
    }

    .forgot-password-link {
      white-space: normal;
    }
  }
}

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
  }

  .auth-footer {
    border-top-color: rgba(255, 255, 255, 0.12);
  }
}

@media (prefers-reduced-motion: reduce) {
  .login-card,
  .gradient-blob {
    animation: none !important;
  }
}
</style>
