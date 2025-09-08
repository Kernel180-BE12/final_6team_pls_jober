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
      >
        이미 계정이 있으신가요? 로그인
      </v-btn>
    </div>
  </v-card>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { authApi } from '@/api'

interface Emits {
  (e: 'switchForm', form: string): void
}

const emit = defineEmits<Emits>()

const username = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const isFormValid = ref(false)
const isLoading = ref(false)
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
</script>

<style scoped>
.register-form {
  max-width: 400px;
  width: 100%;
}
</style>
