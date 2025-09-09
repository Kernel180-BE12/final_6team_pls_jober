import axios from 'axios'

// AI API 기본 설정
const aiApi = axios.create({
  baseURL: '/ai',
  timeout: 30000, // AI 요청은 시간이 오래 걸릴 수 있음
  headers: {
    'Content-Type': 'application/json',
  },
})

// 요청 인터셉터
aiApi.interceptors.request.use(
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
aiApi.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    console.error('AI API Error:', error)
    return Promise.reject(error)
  }
)

// AI 서비스 타입 정의
export interface TemplateGenerationRequest {
  category: string
  user_message: string
  model?: string
}

export interface TemplateGenerationResponse {
  template_content: string
  variables: Array<{
    name: string
    type: string
    description: string
  }>
  category: string
  model: string
}

export interface TemplateModificationRequest {
  current_template: string
  user_message: string
  chat_history?: Array<{
    type: string
    content: string
  }>
}

export interface TemplateModificationResponse {
  modified_template: string
  variables: Array<{
    name: string
    type: string
    description: string
  }>
  explanation: string
  model: string
}

// AI 서비스 함수들
export const aiService = {
  // 템플릿 생성
  async generateTemplate(request: TemplateGenerationRequest): Promise<TemplateGenerationResponse> {
    const response = await aiApi.post('/template/generate', request)
    return response.data
  },

  // 템플릿 수정
  async modifyTemplate(request: TemplateModificationRequest): Promise<TemplateModificationResponse> {
    const response = await aiApi.post('/template/modify', request)
    return response.data
  },

  // OpenAI 채팅
  async chat(message: string, model: string = 'gpt-3.5-turbo'): Promise<string> {
    const response = await aiApi.post('/openai/chat', {
      message,
      model
    })
    return response.data.response
  },

  // 임베딩 생성
  async generateEmbeddings(text: string): Promise<number[]> {
    const response = await aiApi.post('/openai/embeddings', null, {
      params: { text }
    })
    return response.data.embeddings
  },

  // 문서 검색
  async searchDocuments(query: string, n_results: number = 5): Promise<any> {
    const response = await aiApi.post('/chromadb/search', {
      query,
      n_results
    })
    return response.data
  },

  // 헬스 체크
  async healthCheck(): Promise<{ status: string }> {
    const response = await aiApi.get('/health')
    return response.data
  }
}

export default aiService
