import { get, post } from '@/utils/request'
import type { LoginForm, RegisterForm, TokenResponse, User } from '@/types'

// 用户登录
export function login(data: LoginForm) {
  return post<TokenResponse>('/v1/auth/login', data)
}

// 用户注册
export function register(data: RegisterForm) {
  return post('/v1/auth/register', data)
}

// 获取当前用户信息
export function getUserInfo() {
  return get<User>('/v1/auth/me')
}

// 刷新Token
export function refreshToken(refresh_token: string) {
  return post<TokenResponse>('/v1/auth/refresh', { refresh_token })
}

// 更新用户信息
export function updateUserInfo(data: Partial<User>) {
  return post<User>('/v1/auth/me', data)
}

// 修改密码
export function changePassword(data: { old_password: string; new_password: string }) {
  return post('/v1/auth/change-password', data)
}
