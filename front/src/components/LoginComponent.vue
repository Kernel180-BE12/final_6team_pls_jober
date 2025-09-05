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
    
    <div class="text-center">
      <v-btn
        variant="text"
        color="primary"
        @click="$emit('switchForm', 'register')"
        class="mb-2"
      >
        회원가입
      </v-btn>
      <br>
      <v-btn
        variant="text"
        color="secondary"
        @click="$emit('switchForm', 'forgot')"
      >
        비밀번호 찾기
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
const password = ref('')
const isFormValid = ref(false)
const isLoading = ref(false)

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
  try {
    // TODO: 로그인 로직 구현
    console.log('로그인 시도:', { email: email.value, password: password.value })
    await new Promise(resolve => setTimeout(resolve, 1000)) // 임시 딜레이
  } catch (error) {
    console.error('로그인 실패:', error)
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.login-form {
  max-width: 400px;
  width: 100%;
}
</style>
