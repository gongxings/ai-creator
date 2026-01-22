import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { User, TokenResponse } from '@/types'
import * as authApi from '@/api/auth'

export const useUserStore = defineStore('user', () => {
  const token = ref<string>('')
  const refreshToken = ref<string>('')
  const userInfo = ref<User | null>(null)

  // 登录
  const login = async (username: string, password: string) => {
    const res = await authApi.login({ username, password })
    const data = res.data as TokenResponse
    
    token.value = data.access_token
    refreshToken.value = data.refresh_token
    
    // 保存到本地存储
    localStorage.setItem('token', data.access_token)
    localStorage.setItem('refreshToken', data.refresh_token)
    
    // 获取用户信息
    await getUserInfo()
  }

  // 注册
  const register = async (username: string, email: string, password: string) => {
    await authApi.register({ username, email, password, confirm_password: password })
  }

  // 获取用户信息
  const getUserInfo = async () => {
    const res = await authApi.getUserInfo()
    userInfo.value = res.data as User
    localStorage.setItem('userInfo', JSON.stringify(userInfo.value))
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
    login,
    register,
    getUserInfo,
    logout,
    restoreUser
  }
})
