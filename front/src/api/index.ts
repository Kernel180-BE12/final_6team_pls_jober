import axios from 'axios'

// API 기본 설정
const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 요청 인터셉터
api.interceptors.request.use(
  (config) => {
    // 토큰이 있다면 헤더에 추가
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 응답 인터셉터
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    // 401 에러 시 토큰 제거
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
    }
    return Promise.reject(error)
  }
)

export default api

