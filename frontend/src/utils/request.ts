import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'
import { useUserStore } from '@/store/user'
import type { ApiResponse } from '@/types'

// 创建axios实例
const service: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
service.interceptors.request.use(
  (config) => {
    const userStore = useUserStore()
    if (userStore.token) {
      config.headers.Authorization = `Bearer ${userStore.token}`
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
  (response: AxiosResponse<any>) => {
    // 对于登录等特殊接口，直接返回响应数据
    // 因为它们返回的是标准的HTTP 200响应，不是包装过的ApiResponse格式
    return response.data
  },
  (error) => {
    console.error('响应错误:', error)

    let message = '请求失败'
    if (error.response) {
      const status = error.response.status
      switch (status) {
        case 400:
          message = '请求参数错误'
          break
        case 401:
          message = '未授权，请重新登录'
          const userStore = useUserStore()
          userStore.logout()
          router.push('/login')
          break
        case 403:
          message = '拒绝访问'
          break
        case 404:
          message = '请求资源不存在'
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
          message = error.response.data?.message || '请求失败'
      }
    } else if (error.request) {
      message = '网络错误，请检查网络连接'
    }

    ElMessage.error(message)
    return Promise.reject(error)
  }
)

// 封装请求方法
export function request<T = any>(config: AxiosRequestConfig): Promise<ApiResponse<T>> {
  return service.request(config)
}

export function get<T = any>(url: string, params?: any): Promise<ApiResponse<T>> {
  return service.get(url, { params })
}

export function post<T = any>(url: string, data?: any): Promise<ApiResponse<T>> {
  return service.post(url, data)
}

export function put<T = any>(url: string, data?: any): Promise<ApiResponse<T>> {
  return service.put(url, data)
}

export function del<T = any>(url: string): Promise<ApiResponse<T>> {
  return service.delete(url)
}

export default service
