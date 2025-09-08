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
    
    <div class="text-center">
      <v-btn
        variant="text"
        color="primary"
        @click="$emit('switchForm', 'login')"
      >
        로그인으로 돌아가기
      </v-btn>
    </div>
  </v-card>
</template>

<script setup lang="ts">
import { ref } from 'vue'

interface Emits {
  (e: 'switchForm', form: string): void
}

const emit = defineEmits<Emits>()

const email = ref('')
const isFormValid = ref(false)
const isLoading = ref(false)

const emailRules = [
  (v: string) => !!v || '이메일을 입력해주세요',
  (v: string) => /.+@.+\..+/.test(v) || '올바른 이메일 형식을 입력해주세요'
]

const handleForgotPassword = async () => {
  if (!isFormValid.value) return
  
  isLoading.value = true
  try {
    // TODO: 비밀번호 재설정 로직 구현
    console.log('비밀번호 재설정 시도:', { email: email.value })
    await new Promise(resolve => setTimeout(resolve, 1000)) // 임시 딜레이
  } catch (error) {
    console.error('비밀번호 재설정 실패:', error)
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
