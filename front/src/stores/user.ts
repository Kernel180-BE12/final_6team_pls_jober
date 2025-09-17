import { defineStore } from 'pinia'

// 토큰 관리 유틸리티
const TOKEN_KEY = 'access_token'
const REFRESH_TOKEN_KEY = 'refresh_token'
const USER_INFO_KEY = 'user_info'

// 유저 상태 정보 전역 저장
export const useUserStore = defineStore('user', {
  state: () => ({
    accountId: null as number | null, // 유저 ID
    role: null as string | null,      // 유저 역할
    userName: null as string | null,  // 유저 이름
    email: null as string | null,     // 이메일
    accessToken: null as string | null, // 액세스 토큰
    refreshToken: null as string | null, // 리프레시 토큰
  }),
  getters: {
    isLoggedIn: (state) => !!state.accessToken && !!state.accountId,
    isAdmin: (state) => state.role === 'ROLE_ADMIN',
    displayName: (state) => state.userName || state.email || '사용자',
  },
  actions: {
    // 로그인 시 사용자 정보와 토큰 저장
    setUser(user: { 
      accountId: number; 
      role: string; 
      userName?: string; 
      email?: string 
    }, tokens: { accessToken: string; refreshToken: string }) {
      this.accountId = user.accountId
      this.role = user.role
      this.userName = user.userName || null
      this.email = user.email || null
      this.accessToken = tokens.accessToken
      this.refreshToken = tokens.refreshToken
      
      // localStorage에 저장
      localStorage.setItem(TOKEN_KEY, tokens.accessToken)
      localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refreshToken)
      localStorage.setItem(USER_INFO_KEY, JSON.stringify(user))
    },
    
    // 사용자 정보만 업데이트 (토큰은 그대로 유지)
    updateUser(user: { 
      accountId: number; 
      role: string; 
      userName?: string; 
      email?: string 
    }) {
      this.accountId = user.accountId
      this.role = user.role
      this.userName = user.userName || null
      this.email = user.email || null
      localStorage.setItem(USER_INFO_KEY, JSON.stringify(user))
    },
    
    // 토큰 업데이트 (리프레시 토큰으로 새 액세스 토큰 발급 시)
    updateTokens(tokens: { accessToken: string; refreshToken?: string }) {
      this.accessToken = tokens.accessToken
      localStorage.setItem(TOKEN_KEY, tokens.accessToken)
      
      if (tokens.refreshToken) {
        this.refreshToken = tokens.refreshToken
        localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refreshToken)
      }
    },
    
    // 사용자 정보와 토큰 초기화
    clearUser() {
      this.accountId = null
      this.role = null
      this.userName = null
      this.email = null
      this.accessToken = null
      this.refreshToken = null
      
      // localStorage에서 제거
      localStorage.removeItem(TOKEN_KEY)
      localStorage.removeItem(REFRESH_TOKEN_KEY)
      localStorage.removeItem(USER_INFO_KEY)
    },
    
    // 로그아웃

    logout() {
      // 로컬 상태 정리

      this.clearUser()
      // 로그아웃 후 랜딩 페이지로 이동
      window.location.href = '/'
    },
    
    // 페이지 새로고침 시 localStorage에서 사용자 정보 복원
    restoreUser() {
      const accessToken = localStorage.getItem(TOKEN_KEY)
      const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY)
      const userInfoStr = localStorage.getItem(USER_INFO_KEY)
      
      if (accessToken && userInfoStr) {
        try {
          const userInfo = JSON.parse(userInfoStr)
          this.accountId = userInfo.accountId
          this.role = userInfo.role
          this.userName = userInfo.userName || null
          this.email = userInfo.email || null
          this.accessToken = accessToken
          this.refreshToken = refreshToken
        } catch (error) {
          console.error('사용자 정보 복원 실패:', error)
          this.clearUser()
        }
      }
    },
    
    // 토큰 유효성 검사 (선택적)
    async validateToken() {
      if (!this.accessToken) return false
      
      try {
        // 토큰 유효성 검사 API 호출 (실제 구현 시)
        // const response = await api.validateToken(this.accessToken)
        // return response.valid
        
        // 임시로 토큰이 존재하면 유효하다고 가정
        return true
      } catch (error) {
        console.error('토큰 유효성 검사 실패:', error)
        return false
      }
    },
  },
})
