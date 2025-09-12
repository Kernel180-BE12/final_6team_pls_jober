<template>
  <v-card class="forgot-password-form" elevation="0" color="transparent">
    <v-card-title class="text-h4 font-weight-bold text-center mb-6">
      비밀번호 찾기
    </v-card-title>
    
    <v-card-text class="text-center mb-6">
      <p class="text-body-1 text-medium-emphasis">
        가입하신 이메일 주소를 입력하시면<br>
        비밀번호 재설정 링크를 보내드립니다.
      </p>
    </v-card-text>
    
    <v-form @submit.prevent="handleForgotPassword" v-model="isFormValid">
      <v-text-field
        v-model="email"
        label="이메일"
        type="email"
        variant="outlined"
        :rules="emailRules"
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
        비밀번호 재설정
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
        class="w-100"
      >
        로그인으로 돌아가기
      </v-btn>
    </div>
  </v-card>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { authApi } from '@/api'

interface Emits {
  (e: 'switchForm', form: string): void
}

const emit = defineEmits<Emits>()

const email = ref('')
const isFormValid = ref(false)
const isLoading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

const emailRules = [
  (v: string) => !!v || '이메일을 입력해주세요',
  (v: string) => /.+@.+\..+/.test(v) || '올바른 이메일 형식을 입력해주세요'
]

const handleForgotPassword = async () => {
  if (!isFormValid.value) return
  
  isLoading.value = true
  errorMessage.value = ''
  successMessage.value = ''
  
  try {
    const response = await authApi.forgotPassword(email.value)
    
    successMessage.value = '비밀번호 재설정 토큰이 발급되었습니다. 이메일을 확인해주세요.'
    
    // 성공 후 로그인 폼으로 전환
    setTimeout(() => {
      emit('switchForm', 'login')
    }, 3000)
  } catch (error: any) {
    console.error('비밀번호 재설정 실패:', error)
    errorMessage.value = error.response?.data?.message || '비밀번호 재설정 요청에 실패했습니다.'
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.forgot-password-form {
  max-width: 400px;
  width: 100%;
}
</style>
