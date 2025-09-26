import axios from 'axios'
import { useUserStore } from '@/stores/user'

// API 기본 설정
const api = axios.create({
  baseURL: '/api',
  timeout: 30000, // 30초로 증가 (AI 검증 시간 고려)
  headers: {
    'Content-Type': 'application/json',
  },
})

// AI 서비스용 API 설정
const aiApi = axios.create({
  baseURL: '/ai',
  timeout: 60000, // AI 템플릿 생성은 시간이 오래 걸릴 수 있음
  headers: {
    'Content-Type': 'application/json',
  },
})

// 백엔드 API 요청 인터셉터
api.interceptors.request.use(
  (config) => {
    // user store에서 토큰 가져오기
    const userStore = useUserStore()

    // 로그인 관련 API는 토큰이 필요하지 않음
    const isAuthAPI = config.url?.includes('/auth/')
    
    if (!userStore.accessToken && !isAuthAPI) {
      console.warn('API 요청 시 토큰이 없습니다. 로그인이 필요할 수 있습니다.')
    } else if (userStore.accessToken) {
      config.headers.Authorization = `Bearer ${userStore.accessToken}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// AI 서비스 API 요청 인터셉터 (인증 불필요)
aiApi.interceptors.request.use(
  (config) => {
    // AI 서비스는 인증이 필요하지 않음
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 백엔드 API 응답 인터셉터
api.interceptors.response.use(
  (response) => {
    return response
  },
  async (error) => {
    // 401, 403 에러 시 자동 로그아웃
    if (error.response?.status === 401 ) {
      const userStore = useUserStore()
      userStore.logout()
    }
    return Promise.reject(error)
  }
)

// AI 서비스 API 응답 인터셉터 (인증 불필요)
aiApi.interceptors.response.use(
  (response) => {
    return response
  },
  async (error) => {
    // AI 서비스는 인증이 필요하지 않으므로 401 에러 처리 불필요
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
    api.post('/auth/pw/reset', { token, newPassword }),

  // 카카오 로그인 URL 조회
  getKakaoLoginUrl: () =>
    api.get('/auth/kakao/url'),

  // 카카오 로그인 처리
  kakaoLogin: (authorizationCode: string) =>
    api.post('/auth/kakao/login', null, { params: { code: authorizationCode } }),

  // 카카오 로그아웃 URL 조회
  getKakaoLogoutUrl: () =>
    api.post('/auth/kakao/logout'),

  // 로그아웃
  logout: (accessToken: string, refreshToken?: string) =>
    api.post('/auth/logout',
      refreshToken ? { refreshToken } : null,
      {
        headers: {
          'Authorization': `Bearer ${accessToken}`
        }
      }
    )
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

export type VariableDto = { variableKey: string; variableValue: string };

// 템플릿 관련 API
export const templateApi = {
  // AI를 통한 템플릿 생성 (AI 서버 직접 호출)
  generateTemplate: (userMessage: string) => 
    aiApi.post('/template/generate', { userMessage }),
  
  // 템플릿 검증 (백엔드 API를 통해)
  validateTemplate: (templateContent: string, variableList: string[], category?: string, userMessage?: string, templateTitle?: string, templateId?: string) => {
    // variableList가 이미 string[] 형태이므로 그대로 사용
    const variableNames = variableList
    
    // 백엔드 ValidationRequest 형식에 맞게 데이터 변환
    const validationRequest = {
      templateContent: templateContent,
      variableList: variableNames,
      category: category,
      userMessage: userMessage,
      templateTitle: templateTitle,
      templateId: templateId
    }
    
    
    return aiApi.post('/template/validate', validationRequest)
  },
  
  // 템플릿 수정 요청 (채팅을 통한)
  modifyTemplate: (templateContent: string, templateTitle: string, userMessage: string, variableList: string[], category: string, chatHistory: any[]) => {
    const modificationRequest = {
      templateContent: templateContent, 
      templateTitle: templateTitle,
      userMessage: userMessage,
      variableList: variableList,
      category: category,
      chatHistory: chatHistory 
    }
    
    return api.post('/template/modify', modificationRequest)
  },

  // 템플릿 저장 (검증 없이 바로 저장)
  saveTemplate: (templateContent: string, variableList: string[], category: string, userMessage: string, templateTitle: string) => {
    // variableList가 이미 string[] 형태이므로 그대로 사용
    const variableNames = variableList

    const saveRequest = {
      templateContent: templateContent,
      variableList: variableNames,  // 문자열 배열로 직접 전달
      category: category,
      userMessage: userMessage,
      templateTitle: templateTitle
    }


    return api.post('/template/save', saveRequest)
  },
}

// AI 서버 직접 호출용 API (템플릿 생성)
export const aiApiDirect = {
  // AI 서버에 직접 템플릿 생성 요청
  generateTemplate: (userMessage: string) =>
    aiApi.post('/template/generate', { userMessage: userMessage })
}

export { aiApi }
export default api

