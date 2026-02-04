import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User } from '@/types'
import * as authApi from '@/api/auth'
import * as creditApi from '@/api/credit'

export const useUserStore = defineStore('user', () => {
  const token = ref<string>('')
  const refreshToken = ref<string>('')
  const userInfo = ref<User | null>(null)

  // 兼容性计算属性
  const user = computed(() => userInfo.value)
  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => userInfo.value?.role === 'admin')
  // const isLoggedIn = computed(() => true)

  // 登录
  const login = async (username: string, password: string) => {
    const data = await authApi.login({ username, password }) as any
    
    token.value = data.access_token
    refreshToken.value = data.refresh_token
    
    // 保存到本地存储
    localStorage.setItem('token', data.access_token)
    localStorage.setItem('refreshToken', data.refresh_token)
    
    // 登录响应中已经包含用户信息，直接使用
    if (data.user) {
      userInfo.value = data.user as User
      localStorage.setItem('userInfo', JSON.stringify(userInfo.value))
    }
  }

  // 注册
  const register = async (username: string, email: string, password: string) => {
    await authApi.register({ username, email, password, confirm_password: password })
  }

  // 获取用户信息
  const getUserInfo = async () => {
    const data = await authApi.getUserInfo() as any
    userInfo.value = data as User
    localStorage.setItem('userInfo', JSON.stringify(userInfo.value))
  }

  // 更新用户积分和会员信息
  const updateCreditInfo = async () => {
    try {
      const res = await creditApi.getCreditBalance() as any
      if (userInfo.value && res) {
        userInfo.value.credits = res.credits
        userInfo.value.is_member = res.is_member
        userInfo.value.member_expired_at = res.member_expired_at
        localStorage.setItem('userInfo', JSON.stringify(userInfo.value))
      }
    } catch (error) {
      console.error('更新积分信息失败:', error)
    }
  }

  // 登出
  const logout = () => {
    token.value = ''
    refreshToken.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('refreshToken')
    localStorage.removeItem('userInfo')
  }

  // 从本地存储恢复用户信息
  const restoreUser = () => {
    const savedToken = localStorage.getItem('token')
    const savedRefreshToken = localStorage.getItem('refreshToken')
    const savedUserInfo = localStorage.getItem('userInfo')
    
    if (savedToken) {
      token.value = savedToken
    }
    if (savedRefreshToken) {
      refreshToken.value = savedRefreshToken
    }
    if (savedUserInfo) {
      try {
        userInfo.value = JSON.parse(savedUserInfo)
      } catch (e) {
        console.error('解析用户信息失败:', e)
      }
    }
  }

  return {
    token,
    refreshToken,
    userInfo,
    user,
    isLoggedIn,
    isAdmin,
    login,
    register,
    getUserInfo,
    updateCreditInfo,
    logout,
    restoreUser
  }
})
