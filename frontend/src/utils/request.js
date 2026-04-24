/* axios请求封装 */
import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

const request = axios.create({
  baseURL: '/api',
  timeout: 30000
})

/* 请求拦截器，自动添加token */
request.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

/* 响应拦截器，统一处理错误 */
request.interceptors.response.use(
  response => response.data,
  error => {
    if (error.response) {
      const { status, data } = error.response
      if (status === 401) {
        // 登录接口的401直接返回数据，不跳转
        if (error.config.url?.includes('/auth/login')) {
          return Promise.resolve(data)
        }
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        router.push('/login')
        ElMessage.error('登录已过期，请重新登录')
      } else if (status === 403) {
        // 登录接口的403也直接返回
        if (error.config.url?.includes('/auth/login')) {
          return Promise.resolve(data)
        }
        ElMessage.error('没有操作权限')
      } else {
        ElMessage.error(data?.message || '请求失败')
      }
    } else {
      ElMessage.error('网络连接失败')
    }
    return Promise.reject(error)
  }
)

export default request
