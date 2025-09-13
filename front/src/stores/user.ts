import { defineStore } from 'pinia'

// 유저 상태 정보 전역 저장
export const useUserStore = defineStore('user', {
  state: () => ({
    accountId: null as number | null, // 유저 ID
    role: null as string | null,      // 유저 역할
  }),
  getters: {
    isLoggedIn: (state) => !!state.accountId,
    isAdmin: (state) => state.role === 'ROLE_ADMIN',
  },
  actions: {
    setUser(user: { accountId: number; role: string }) {
      this.accountId = user.accountId
      this.role = user.role
    },
    clearUser() {
      this.accountId = null
      this.role = null
    },
  },
})
