/**
 * Axios请求封装
 */
import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/store/user'
import router from '@/router'

// 不需要登录验证的接口白名单
const whiteList = [
  '/api/v1/auth/login',
  '/api/v1/auth/register',
  '/api/v1/auth/refresh',
]

// 创建axios实例
const service: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 是否正在显示登录提示
let isShowingLoginPrompt = false

// 请求拦截器
service.interceptors.request.use(
  async (config) => {
    const userStore = useUserStore()
    const token = userStore.token
    
    // 检查是否在白名单中
    const isWhiteListed = whiteList.some(path => config.url?.includes(path))
    
    // 如果不在白名单中且未登录，提示用户
    if (!isWhiteListed && !token && !isShowingLoginPrompt) {
      isShowingLoginPrompt = true
      
      try {
        await ElMessageBox.confirm(
          '您还未登录，是否跳转到登录页面？',
          '未登录提示',
          {
            confirmButtonText: '去登录',
            cancelButtonText: '取消',
            type: 'warning',
          }
        )
        
        // 用户确认跳转到登录页
        router.push({
          path: '/login',
          query: {
            redirect: router.currentRoute.value.fullPath
          }
        })
        
        isShowingLoginPrompt = false
        return Promise.reject(new Error('用户未登录'))
      } catch {
        // 用户取消
        isShowingLoginPrompt = false
        return Promise.reject(new Error('用户取消登录'))
      }
    }
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    return config
  },
  (error) => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  (response: AxiosResponse) => {
    const res = response.data
    
    // 如果返回的状态码不是200，则认为是错误
    if (res.code !== 200) {
      ElMessage.error(res.message || '请求失败')
      
      // 401: 未授权，跳转到登录页
      if (res.code === 401) {
        const userStore = useUserStore()
        userStore.logout()
        
        if (!isShowingLoginPrompt) {
          isShowingLoginPrompt = true
          ElMessageBox.confirm(
            '登录已过期，请重新登录',
            '登录过期',
            {
              confirmButtonText: '重新登录',
              cancelButtonText: '取消',
              type: 'warning',
            }
          ).then(() => {
            router.push({
              path: '/login',
              query: {
                redirect: router.currentRoute.value.fullPath
              }
            })
          }).finally(() => {
            isShowingLoginPrompt = false
          })
        }
      }
      
      return Promise.reject(new Error(res.message || '请求失败'))
    }
    
    return res
  },
  (error) => {
    console.error('响应错误:', error)
    
    let message = '请求失败'
    
    if (error.response) {
      const status = error.response.status
      
      switch (status) {
        case 400:
          message = error.response.data.detail || '请求参数错误'
          break
        case 401:
          message = '未授权，请重新登录'
          const userStore = useUserStore()
          userStore.logout()
          
          if (!isShowingLoginPrompt) {
            isShowingLoginPrompt = true
            ElMessageBox.confirm(
              '登录已过期，请重新登录',
              '登录过期',
              {
                confirmButtonText: '重新登录',
                cancelButtonText: '取消',
                type: 'warning',
              }
            ).then(() => {
              router.push({
                path: '/login',
                query: {
                  redirect: router.currentRoute.value.fullPath
                }
              })
            }).finally(() => {
              isShowingLoginPrompt = false
            })
          }
          break
        case 403:
          message = '拒绝访问'
          break
        case 404:
          message = '请求的资源不存在'
          break
        case 429:
          message = '请求过于频繁，请稍后再试'
          break
        case 500:
          message = '服务器内部错误'
          break
        case 503:
          message = '服务暂时不可用'
          break
        default:
          message = error.response.data.detail || `请求失败 (${status})`
      }
    } else if (error.request) {
      message = '网络错误，请检查网络连接'
    }
    
    ElMessage.error(message)
    return Promise.reject(error)
  }
)

export default service
