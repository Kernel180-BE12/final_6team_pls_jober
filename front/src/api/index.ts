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
    const token = localStorage.getItem('accessToken')
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
      localStorage.removeItem('accessToken')
      localStorage.removeItem('refreshToken')
    }
    return Promise.reject(error)
  }
)

// 인증 관련 API
export const authApi = {
  // 로그인
  login: (email: string, password: string) => 
    api.post('/auth/login', { email, password }),
  
  // 회원가입
  signup: (username: string, email: string, password: string) => 
    api.post('/auth/signup', { username, email, password }),
  
  // 비밀번호 재설정 요청
  forgotPassword: (email: string) => 
    api.post('/auth/pw/request', { email }),
  
  // 비밀번호 재설정
  resetPassword: (token: string, newPassword: string) => 
    api.post('/auth/pw/reset', { token, newPassword })
}

// 마이페이지 관련 API
export const myPageApi = {
  // 내 정보 조회
  getMyInfo: () => api.get('/mypage'),
  
  // 이름 수정
  updateName: (name: string) => api.put('/mypage/name', { name }),
  
  // 이메일 변경
  updateEmail: (email: string, currentPassword: string) => 
    api.put('/mypage/email', { email, currentPassword }),
  
  // 비밀번호 변경
  updatePassword: (currentPassword: string, newPassword: string, confirmPassword: string) =>
    api.put('/mypage/password', { currentPassword, newPassword, confirmPassword })
}

export default api

