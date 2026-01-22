<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <h1>AI创作者平台</h1>
        <p>让创作更简单，让灵感更自由</p>
      </div>

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
            @keyup.enter="handleLogin"
          />
        </el-form-item>

        <el-form-item>
          <el-checkbox v-model="loginForm.remember">记住我</el-checkbox>
          <el-link type="primary" :underline="false" class="forgot-password">
            忘记密码？
          </el-link>
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            class="login-button"
            @click="handleLogin"
          >
            登录
          </el-button>
        </el-form-item>

        <el-form-item class="register-link">
          <span>还没有账号？</span>
          <el-link type="primary" :underline="false" @click="goToRegister">
            立即注册
          </el-link>
        </el-form-item>
      </el-form>
    </div>
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
      await userStore.login({
        username: loginForm.username,
        password: loginForm.password,
      })

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
</script>

<style scoped lang="scss">
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-box {
  width: 420px;
  padding: 40px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.login-header {
  text-align: center;
  margin-bottom: 40px;

  h1 {
    font-size: 28px;
    font-weight: 600;
    color: #333;
    margin-bottom: 8px;
  }

  p {
    font-size: 14px;
    color: #666;
  }
}

.login-form {
  .el-form-item {
    margin-bottom: 24px;

    &:last-child {
      margin-bottom: 0;
    }
  }

  .forgot-password {
    float: right;
    font-size: 14px;
  }

  .login-button {
    width: 100%;
    height: 44px;
    font-size: 16px;
    font-weight: 500;
  }

  .register-link {
    text-align: center;
    font-size: 14px;

    span {
      color: #666;
      margin-right: 8px;
    }
  }
}
</style>
