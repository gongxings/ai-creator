<template>
  <div class="register-container">
    <div class="background-decoration">
      <div class="gradient-blob blob-1"></div>
      <div class="gradient-blob blob-2"></div>
    </div>

    <div class="register-content">
      <div class="register-card">
        <section class="intro-panel">
          <div class="intro-badge">新用户欢迎</div>
          <h1>创建你的 AI 创作空间</h1>
          <p>统一接入写作、图片、视频与发布工具，注册后即可开始使用。</p>
          <ul class="intro-list">
            <li>统一工作台和创作记录</li>
            <li>会员、积分和多平台能力集中管理</li>
            <li>移动端优先优化，注册后立即可用</li>
          </ul>
        </section>

        <section class="form-panel">
          <div class="form-header">
            <h2>注册账号</h2>
            <p>开启你的 AI 创作之旅</p>
          </div>

          <el-form
            ref="registerFormRef"
            :model="registerForm"
            :rules="registerRules"
            class="register-form"
            @submit.prevent="handleRegister"
          >
            <el-form-item prop="username">
              <el-input
                v-model="registerForm.username"
                placeholder="用户名（4-20个字符）"
                size="large"
                :prefix-icon="User"
              />
            </el-form-item>

            <el-form-item prop="email">
              <el-input
                v-model="registerForm.email"
                placeholder="邮箱地址"
                size="large"
                :prefix-icon="Message"
              />
            </el-form-item>

            <el-form-item prop="password">
              <el-input
                v-model="registerForm.password"
                type="password"
                placeholder="密码（至少 6 位）"
                size="large"
                :prefix-icon="Lock"
                show-password
              />
            </el-form-item>

            <el-form-item prop="confirmPassword">
              <el-input
                v-model="registerForm.confirmPassword"
                type="password"
                placeholder="确认密码"
                size="large"
                :prefix-icon="Lock"
                show-password
                @keyup.enter="handleRegister"
              />
            </el-form-item>

            <el-form-item prop="agree" class="agree-item">
              <el-checkbox v-model="registerForm.agree">
                我已阅读并同意
                <el-link type="primary" :underline="false">《用户协议》</el-link>
                和
                <el-link type="primary" :underline="false">《隐私政策》</el-link>
              </el-checkbox>
            </el-form-item>

            <el-form-item>
              <el-button
                type="primary"
                size="large"
                :loading="loading"
                class="register-button"
                @click="handleRegister"
              >
                {{ loading ? '注册中...' : '立即注册' }}
              </el-button>
            </el-form-item>

            <div class="login-link">
              <span>已有账号？</span>
              <el-link type="primary" :underline="false" @click="goToLogin">立即登录</el-link>
            </div>
          </el-form>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { User, Lock, Message } from '@element-plus/icons-vue'
import { register } from '@/api/auth'

const router = useRouter()

const registerFormRef = ref<FormInstance>()
const loading = ref(false)

const registerForm = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  agree: false,
})

const validateUsername = (_rule: any, value: string, callback: any) => {
  if (!value) {
    callback(new Error('请输入用户名'))
  } else if (value.length < 4 || value.length > 20) {
    callback(new Error('用户名长度为4-20个字符'))
  } else if (!/^[a-zA-Z0-9_]+$/.test(value)) {
    callback(new Error('用户名只能包含字母、数字和下划线'))
  } else {
    callback()
  }
}

const validateEmail = (_rule: any, value: string, callback: any) => {
  if (!value) {
    callback(new Error('请输入邮箱地址'))
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
    callback(new Error('请输入有效的邮箱地址'))
  } else {
    callback()
  }
}

const validatePassword = (_rule: any, value: string, callback: any) => {
  if (!value) {
    callback(new Error('请输入密码'))
  } else if (value.length < 6) {
    callback(new Error('密码长度不能少于6位'))
  } else {
    if (registerForm.confirmPassword) {
      registerFormRef.value?.validateField('confirmPassword')
    }
    callback()
  }
}

const validateConfirmPassword = (_rule: any, value: string, callback: any) => {
  if (!value) {
    callback(new Error('请再次输入密码'))
  } else if (value !== registerForm.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const validateAgree = (_rule: any, value: boolean, callback: any) => {
  if (!value) {
    callback(new Error('请阅读并同意用户协议和隐私政策'))
  } else {
    callback()
  }
}

const registerRules: FormRules = {
  username: [{ validator: validateUsername, trigger: 'blur' }],
  email: [{ validator: validateEmail, trigger: 'blur' }],
  password: [{ validator: validatePassword, trigger: 'blur' }],
  confirmPassword: [{ validator: validateConfirmPassword, trigger: 'blur' }],
  agree: [{ validator: validateAgree, trigger: 'change' }],
}

const handleRegister = async () => {
  if (!registerFormRef.value) return

  await registerFormRef.value.validate(async (valid) => {
    if (!valid) return

    loading.value = true
    try {
      await register({
        username: registerForm.username,
        email: registerForm.email,
        password: registerForm.password,
      })
      ElMessage.success('注册成功，请登录')
      router.push('/login')
    } catch (error: any) {
      ElMessage.error(error.message || '注册失败，请稍后重试')
    } finally {
      loading.value = false
    }
  })
}

const goToLogin = () => {
  router.push('/login')
}
</script>

<style scoped lang="scss">
$primary-color: #2563eb;
$secondary-color: #38bdf8;
$text-primary: #0f172a;
$text-secondary: #5b6472;

.register-container {
  position: relative;
  min-height: 100dvh;
  overflow: hidden;
  background:
    radial-gradient(1200px circle at -10% -20%, rgba(56, 189, 248, 0.28) 0%, transparent 60%),
    radial-gradient(900px circle at 110% 0%, rgba(37, 99, 235, 0.24) 0%, transparent 55%),
    linear-gradient(135deg, #f6f8ff 0%, #eef6ff 45%, #f3fbff 100%);
}

.background-decoration {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.gradient-blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.36;

  &.blob-1 {
    width: 320px;
    height: 320px;
    left: -100px;
    top: -100px;
    background: rgba(56, 189, 248, 0.35);
  }

  &.blob-2 {
    width: 260px;
    height: 260px;
    right: -80px;
    bottom: -70px;
    background: rgba(37, 99, 235, 0.28);
  }
}

.register-content {
  position: relative;
  z-index: 1;
  min-height: 100dvh;
  padding: 24px 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.register-card {
  width: min(1120px, 100%);
  display: grid;
  grid-template-columns: minmax(0, 0.95fr) minmax(0, 1.05fr);
  overflow: hidden;
  border-radius: 26px;
  border: 1px solid rgba(255, 255, 255, 0.6);
  background: rgba(255, 255, 255, 0.84);
  box-shadow: 0 28px 60px rgba(15, 23, 42, 0.16);
  backdrop-filter: blur(18px) saturate(1.08);
}

.intro-panel {
  padding: 44px 38px;
  color: $text-primary;
  background:
    linear-gradient(145deg, rgba(37, 99, 235, 0.18), rgba(56, 189, 248, 0.12)),
    radial-gradient(180px circle at 20% 18%, rgba(37, 99, 235, 0.18), transparent 70%);

  .intro-badge {
    display: inline-flex;
    margin-bottom: 18px;
    padding: 8px 14px;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.7);
    border: 1px solid rgba(37, 99, 235, 0.16);
    color: $primary-color;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.04em;
  }

  h1 {
    margin: 0 0 14px;
    font-size: 36px;
    line-height: 1.1;
  }

  p {
    margin: 0 0 22px;
    color: $text-secondary;
    line-height: 1.7;
  }
}

.intro-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 12px;

  li {
    padding: 14px 16px;
    border-radius: 16px;
    background: rgba(255, 255, 255, 0.72);
    border: 1px solid rgba(37, 99, 235, 0.12);
    box-shadow: 0 10px 20px rgba(37, 99, 235, 0.08);
  }
}

.form-panel {
  padding: 44px 42px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.95), rgba(239, 246, 255, 0.92));
}

.form-header {
  margin-bottom: 24px;

  h2 {
    margin: 0 0 6px;
    font-size: 28px;
    color: $text-primary;
  }

  p {
    margin: 0;
    font-size: 14px;
    color: $text-secondary;
  }
}

.register-form {
  :deep(.el-form-item__content),
  :deep(.el-input) {
    width: 100%;
  }

  .el-form-item {
    margin-bottom: 18px;

    :deep(.el-input__wrapper) {
      border-radius: 12px;
      background: rgba(255, 255, 255, 0.86);
      border: 1px solid rgba(37, 99, 235, 0.14);
      box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.4), 0 8px 16px rgba(37, 99, 235, 0.08);
    }
  }

  .agree-item {
    margin-bottom: 10px;

    :deep(.el-checkbox) {
      white-space: normal;
      line-height: 1.7;
    }

    :deep(.el-checkbox__label) {
      color: $text-secondary;
    }
  }

  .register-button {
    width: 100%;
    height: 46px;
    border: none;
    border-radius: 12px;
    font-size: 16px;
    font-weight: 600;
    background: linear-gradient(135deg, $primary-color 0%, #0ea5e9 45%, $secondary-color 100%);
  }
}

.login-link {
  text-align: center;
  font-size: 14px;
  color: $text-secondary;

  span {
    margin-right: 4px;
  }
}

@media (max-width: 900px) {
  .register-content {
    padding: 20px;
  }

  .register-card {
    grid-template-columns: 1fr;
  }

  .intro-panel {
    padding: 32px;
  }

  .form-panel {
    padding: 32px;
  }
}

@media (max-width: 600px) {
  .register-content {
    padding: 12px;
    align-items: flex-start;
  }

  .register-card {
    border-radius: 18px;
  }

  .intro-panel {
    padding: 22px 20px 18px;

    h1 {
      font-size: 26px;
    }
  }

  .intro-list li {
    padding: 12px 14px;
    border-radius: 14px;
    font-size: 13px;
  }

  .form-panel {
    padding: 22px 20px 20px;
  }

  .form-header {
    margin-bottom: 18px;

    h2 {
      font-size: 22px;
    }
  }
}
</style>
