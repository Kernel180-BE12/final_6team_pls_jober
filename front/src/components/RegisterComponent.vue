<template>
  <v-card class="register-form" elevation="0" color="transparent">
    <v-card-title class="text-h4 font-weight-bold text-center mb-6">
      회원가입
    </v-card-title>
    
    <v-form @submit.prevent="handleRegister" v-model="isFormValid">
      <v-text-field
        v-model="username"
        label="사용자 이름"
        variant="outlined"
        :rules="usernameRules"
        required
        class="mb-4"
      />
      
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
        class="mb-4"
      />
      
      <v-text-field
        v-model="confirmPassword"
        label="비밀번호 확인"
        type="password"
        variant="outlined"
        :rules="confirmPasswordRules"
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
        회원가입
      </v-btn>
    </v-form>

    <!-- 소셜 로그인 구분선 -->
    <v-divider class="my-4">
      <span class="text-caption text-medium-emphasis">또는</span>
    </v-divider>

    <!-- 카카오 회원가입 버튼 -->
    <v-btn
      color="#FEE500"
      size="large"
      block
      :loading="isKakaoLoading"
      @click="handleKakaoSignup"
      class="mb-4 text-black"
      style="background-color: #FEE500 !important;"
    >
      <v-icon start>mdi-chat</v-icon>
      카카오로 회원가입
    </v-btn>
    
    <!-- 성공 메시지 표시 -->
    <v-alert
      v-if="successMessage"
      type="success"
      variant="tonal"
      class="mb-4"
    >
      {{ successMessage }}
    </v-alert>
    
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
        @click="$emit('switchForm', 'login')"
        class="w-100"
      >
        이미 계정이 있으신가요? 로그인
      </v-btn>
    </div>
  </v-card>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
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

const username = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const isFormValid = ref(false)
const isLoading = ref(false)
const isKakaoLoading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

const usernameRules = [
  (v: string) => !!v || '사용자 이름을 입력해주세요',
  (v: string) => v.length >= 2 || '사용자 이름은 최소 2자 이상이어야 합니다'
]

const emailRules = [
  (v: string) => !!v || '이메일을 입력해주세요',
  (v: string) => /.+@.+\..+/.test(v) || '올바른 이메일 형식을 입력해주세요'
]

const passwordRules = [
  (v: string) => !!v || '비밀번호를 입력해주세요',
  (v: string) => v.length >= 8 || '비밀번호는 최소 8자 이상이어야 합니다'
]

const confirmPasswordRules = [
  (v: string) => !!v || '비밀번호 확인을 입력해주세요',
  (v: string) => v === password.value || '비밀번호가 일치하지 않습니다'
]

const handleRegister = async () => {
  if (!isFormValid.value) return

  isLoading.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    const response = await authApi.signup(username.value, email.value, password.value)

    successMessage.value = '회원가입이 완료되었습니다. 로그인해주세요.'

    // 성공 후 로그인 폼으로 전환
    setTimeout(() => {
      emit('switchForm', 'login')
    }, 2000)
  } catch (error: any) {
    console.error('회원가입 실패:', error)
    errorMessage.value = error.response?.data?.message || '회원가입에 실패했습니다.'
  } finally {
    isLoading.value = false
  }
}

const handleKakaoSignup = async () => {
  isKakaoLoading.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    // 카카오 로그인 URL 조회
    const urlResponse = await authApi.getKakaoLoginUrl()
    const kakaoAuthUrl = urlResponse.data.url

    // 새 창에서 카카오 로그인 페이지 열기
    const kakaoWindow = window.open(
      kakaoAuthUrl,
      'kakaoSignup',
      'width=500,height=600,scrollbars=yes,resizable=yes'
    )

    // 메시지 이벤트 리스너 등록
    const messageListener = async (event: MessageEvent) => {
      if (event.origin !== window.location.origin) return

      if (event.data.type === 'KAKAO_LOGIN_SUCCESS') {
        kakaoWindow?.close()
        window.removeEventListener('message', messageListener)

        try {
          // 카카오 로그인/회원가입 처리
          const response = await authApi.kakaoLogin(event.data.code)

          // 토큰 저장
          localStorage.setItem('accessToken', response.data.accessToken)
          localStorage.setItem('refreshToken', response.data.refreshToken)

          // 회원가입 성공 메시지 표시
          successMessage.value = '카카오 회원가입이 완료되었습니다!'

          // 랜딩 페이지 showForm 비활성화
          emit('loginSuccess')

          // 전역 유저 상태 업데이트
          userStore.setUser({
            accountId: response.data.userId,
            role: response.data.role
          })

          // 회원가입 성공 시 랜딩 페이지로 이동
          setTimeout(() => {
            router.push('/')
          }, 1500)
        } catch (error: any) {
          console.error('카카오 회원가입 처리 실패:', error)
          errorMessage.value = error.response?.data?.message || '카카오 회원가입에 실패했습니다.'
        }
      } else if (event.data.type === 'KAKAO_LOGIN_ERROR') {
        kakaoWindow?.close()
        window.removeEventListener('message', messageListener)
        errorMessage.value = '카카오 회원가입이 취소되었습니다.'
      }
    }

    window.addEventListener('message', messageListener)

    // 창이 닫혔는지 주기적으로 확인
    const checkClosed = setInterval(() => {
      if (kakaoWindow?.closed) {
        clearInterval(checkClosed)
        window.removeEventListener('message', messageListener)
        isKakaoLoading.value = false
      }
    }, 1000)

  } catch (error: any) {
    console.error('카카오 회원가입 URL 조회 실패:', error)
    errorMessage.value = '카카오 회원가입을 시작할 수 없습니다.'
  } finally {
    isKakaoLoading.value = false
  }
}
</script>

<style scoped>
.register-form {
  max-width: 400px;
  width: 100%;
}
</style>
