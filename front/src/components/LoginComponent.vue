<template>
  <v-card class="login-form" elevation="0" color="transparent">
    <v-card-title class="text-h4 font-weight-bold text-center mb-6">
      로그인
    </v-card-title>
    
    <v-form @submit.prevent="handleLogin" v-model="isFormValid">
      <v-text-field
        v-model="email"
        label="이메일"
        type="email"
        variant="outlined"
        :rules="emailRules"
        required
        class="mb-4"
      />
      
      <v-text-field
        v-model="password"
        label="비밀번호"
        type="password"
        variant="outlined"
        :rules="passwordRules"
        required
        class="mb-6"
      />
      
      <v-btn
        type="submit"
        color="primary"
        size="large"
        block
        :loading="isLoading"
        :disabled="!isFormValid"
        class="mb-4"
      >
        로그인
      </v-btn>
    </v-form>

    <!-- 카카오 로그인 버튼 -->
    <v-divider class="mb-4">
      <span class="text-grey-500">또는</span>
    </v-divider>

    <v-btn
      @click="handleKakaoLogin"
      color="#FEE500"
      size="large"
      block
      :loading="isKakaoLoading"
      class="mb-4 kakao-btn"
    >
      <v-icon start>mdi-chat</v-icon>
      카카오로 로그인
    </v-btn>
    
    <!-- 에러 메시지 표시 -->
    <v-alert
      v-if="errorMessage"
      type="error"
      variant="tonal"
      class="mb-4"
    >
      {{ errorMessage }}
    </v-alert>
    
    <div class="text-center">
      <v-btn
        variant="text"
        color="primary"
        @click="$emit('switchForm', 'register')"
        class="mb-2 w-100"
      >
        회원가입
      </v-btn>
      <br>
      <v-btn
        variant="text"
        color="secondary"
        @click="$emit('switchForm', 'forgot')"
        class="w-100"
      >
        비밀번호 찾기
      </v-btn>
    </div>
  </v-card>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { authApi } from '@/api'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

interface Emits {
  (e: 'switchForm', form: string): void
  (e: 'loginSuccess'): void
}

const emit = defineEmits<Emits>()
const router = useRouter()
const userStore = useUserStore()

const email = ref('')
const password = ref('')
const isFormValid = ref(false)
const isLoading = ref(false)
const isKakaoLoading = ref(false)
const errorMessage = ref('')

const emailRules = [
  (v: string) => !!v || '이메일을 입력해주세요',
  (v: string) => /.+@.+\..+/.test(v) || '올바른 이메일 형식을 입력해주세요'
]

const passwordRules = [
  (v: string) => !!v || '비밀번호를 입력해주세요',
  (v: string) => v.length >= 6 || '비밀번호는 최소 6자 이상이어야 합니다'
]

const handleLogin = async () => {
  if (!isFormValid.value) return

  isLoading.value = true
  errorMessage.value = ''

  try {
    const response = await authApi.login(email.value, password.value)

    // 랜딩 페이지 showForm 비활성화
    emit('loginSuccess')

    // 전역 유저 상태와 토큰 저장
    userStore.setUser(
      {
        accountId: response.data.userId,
        role: response.data.role
      },
      {
        accessToken: response.data.accessToken,
        refreshToken: response.data.refreshToken
      }
    )

    // 로그인 성공 시 랜딩 페이지로 이동
    router.push('/')
  } catch (error: any) {
    console.error('로그인 실패:', error)
    errorMessage.value = error.response?.data?.message || '로그인에 실패했습니다.'
  } finally {
    isLoading.value = false
  }
}

const handleKakaoLogin = async () => {
  isKakaoLoading.value = true
  errorMessage.value = ''

  try {
    // 백엔드에서 카카오 로그인 URL 가져오기
    const response = await authApi.getKakaoLoginUrl()

    // 카카오 로그인 페이지로 리다이렉트
    window.location.href = response.data.url
  } catch (error: any) {
    console.error('카카오 로그인 실패:', error)
    errorMessage.value = '카카오 로그인에 실패했습니다.'
  } finally {
    isKakaoLoading.value = false
  }
}
</script>

<style scoped>
.login-form {
  max-width: 400px;
  width: 100%;
}

.kakao-btn {
  color: #000000 !important;
  text-transform: none !important;
  font-weight: 600 !important;
}
</style>
