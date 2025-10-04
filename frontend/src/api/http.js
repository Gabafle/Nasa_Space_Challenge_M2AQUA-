import axios from 'axios'
import { useAuth } from '../stores/auth'
import { useToast } from '../stores/toast'

const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || 'http://localhost:5000',
  timeout: 30000
})

// Request interceptor
http.interceptors.request.use(config => {
  const auth = useAuth()
  if (auth.accessToken) {
    config.headers.Authorization = `Bearer ${auth.accessToken}`
  }
  return config
})

// Response interceptor
http.interceptors.response.use(
  response => response,
  async error => {
    const auth = useAuth()
    const toast = useToast()
    
    if (error.response?.status === 401 && auth.refreshToken) {
      try {
        const { data } = await axios.post(
          `${http.defaults.baseURL}/api/auth/refresh`,
          {},
          { headers: { Authorization: `Bearer ${auth.refreshToken}` } }
        )
        auth.setAccessToken(data.access_token)
        error.config.headers.Authorization = `Bearer ${data.access_token}`
        return http.request(error.config)
      } catch {
        auth.logout()
        window.location.href = '/login'
      }
    }
    
    // Show error message
    if (error.response?.data?.error) {
      toast.error(error.response.data.error)
    } else if (!error.response) {
      toast.error('Network error - please check your connection')
    }
    
    return Promise.reject(error)
  }
)

export default http