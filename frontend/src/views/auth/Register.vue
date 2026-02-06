<template>
  <div class="register-container flagship-page page-shell">
    <section class="page-hero register-hero">
      <div class="hero-grid">
        <div class="hero-main">
          <span class="hero-eyebrow">Join Us</span>
          <h1 class="hero-title">注册账号</h1>
          <p class="hero-subtitle">开启你的AI创作之旅，写作、图片、视频全场景支持。</p>
          <div class="hero-actions">
            <el-button type="primary" :loading="loading" @click="handleRegister">立即注册</el-button>
            <el-button @click="goToLogin">已有账号</el-button>
          </div>
        </div>
        <div class="hero-panel">
          <div class="hero-panel-title">注册后你将获得</div>
          <div class="hero-stats">
            <div class="hero-stat">
              <div class="hero-stat-value">14</div>
              <div class="hero-stat-label">写作工具</div>
            </div>
            <div class="hero-stat">
              <div class="hero-stat-value">3</div>
              <div class="hero-stat-label">多媒体能力</div>
            </div>
            <div class="hero-stat">
              <div class="hero-stat-value">多平台</div>
              <div class="hero-stat-label">一键发布</div>
            </div>
            <div class="hero-stat">
              <div class="hero-stat-value">模板库</div>
              <div class="hero-stat-label">快速起稿</div>
            </div>
          </div>
          <div class="hero-tags">
            <span class="hero-tag">创意写作</span>
            <span class="hero-tag">多媒体生成</span>
            <span class="hero-tag">内容发布</span>
          </div>
        </div>
      </div>
    </section>

    <section class="page-dashboard">
      <div class="dashboard-grid">
        <div class="dashboard-card">
          <div class="label">内容工具</div>
          <div class="value">14+</div>
          <div class="delta">覆盖多种写作场景</div>
        </div>
        <div class="dashboard-card">
          <div class="label">多媒体能力</div>
          <div class="value">图片 / 视频</div>
          <div class="delta">支持多模态创作</div>
        </div>
        <div class="dashboard-card">
          <div class="label">发布效率</div>
          <div class="value">一键多平台</div>
          <div class="delta">内容触达更广</div>
        </div>
      </div>
    </section>

    <section class="page-body">
      <div class="main-panel">
        <div class="panel register-panel">
          <div class="panel-title">创建账号</div>
          <p class="panel-subtitle">填写基本信息即可开始使用</p>
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
                placeholder="密码（至少6位）"
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

            <el-form-item prop="agree">
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
                注册
              </el-button>
            </el-form-item>

            <el-form-item class="login-link">
              <span>已有账号？</span>
              <el-link type="primary" :underline="false" @click="goToLogin">
                立即登录
              </el-link>
            </el-form-item>
          </el-form>
        </div>
      </div>
      <aside class="side-panel">
        <div class="panel">
          <h3 class="panel-title">注册优势</h3>
          <p class="panel-subtitle">注册后可解锁完整创作流程</p>
          <div class="info-list">
            <div class="info-item">
              <div class="info-icon"><el-icon><User /></el-icon></div>
              <div>
                <div class="info-title">个性化空间</div>
                <div class="info-desc">保存创作历史与偏好设置。</div>
              </div>
            </div>
            <div class="info-item">
              <div class="info-icon"><el-icon><Lock /></el-icon></div>
              <div>
                <div class="info-title">账号安全</div>
                <div class="info-desc">支持绑定邮箱与多平台授权。</div>
              </div>
            </div>
            <div class="info-item">
              <div class="info-icon"><el-icon><Message /></el-icon></div>
              <div>
                <div class="info-title">创作支持</div>
                <div class="info-desc">享受新功能与专属提示。</div>
              </div>
            </div>
          </div>
        </div>
      </aside>
    </section>
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

const validateUsername = (rule: any, value: string, callback: any) => {
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

const validateEmail = (rule: any, value: string, callback: any) => {
  if (!value) {
    callback(new Error('请输入邮箱地址'))
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
    callback(new Error('请输入有效的邮箱地址'))
  } else {
    callback()
  }
}

const validatePassword = (rule: any, value: string, callback: any) => {
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

const validateConfirmPassword = (rule: any, value: string, callback: any) => {
  if (!value) {
    callback(new Error('请再次输入密码'))
  } else if (value !== registerForm.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const validateAgree = (rule: any, value: boolean, callback: any) => {
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
.register-container {
  min-height: 100dvh;
  padding: 32px 24px;
  background:
    radial-gradient(1000px circle at 10% -10%, rgba(56, 189, 248, 0.25) 0%, transparent 60%),
    radial-gradient(900px circle at 100% 0%, rgba(37, 99, 235, 0.2) 0%, transparent 55%),
    linear-gradient(135deg, #f5f8ff 0%, #eef6ff 45%, #f3fbff 100%);
  --hero-from: rgba(37, 99, 235, 0.2);
  --hero-to: rgba(14, 165, 233, 0.18);
  --page-accent: #2563eb;

  .register-panel {
    background: rgba(255, 255, 255, 0.9);
    border: 1px solid rgba(37, 99, 235, 0.18);
    box-shadow: 0 22px 48px rgba(15, 23, 42, 0.14);
    border-radius: 22px;
  }

  .register-form {
    .el-form-item {
      margin-bottom: 20px;

      &:last-child {
        margin-bottom: 0;
      }
    }

    .register-button {
      width: 100%;
      height: 44px;
      font-size: 16px;
      font-weight: 600;
    }

    .login-link {
      text-align: center;
      font-size: 14px;

      span {
        color: #666;
        margin-right: 8px;
      }
    }
  }
}

@media (max-width: 768px) {
  .register-container {
    padding: 20px 16px;

    .register-panel {
      border-radius: 18px;
      padding: 20px;
    }
  }
}
</style>
