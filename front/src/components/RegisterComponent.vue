<template>
  <v-card class="register-form" elevation="0" color="transparent">
    <v-card-title class="text-h4 font-weight-bold text-center mb-6">
      회원가입
    </v-card-title>
    
    <v-form @submit.prevent="handleRegister" v-model="isFormValid">
      <v-text-field
        v-model="name"
        label="이름"
        variant="outlined"
        :rules="nameRules"
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

interface Emits {
  (e: 'switchForm', form: string): void
}

const emit = defineEmits<Emits>()

const name = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const isFormValid = ref(false)
const isLoading = ref(false)

const nameRules = [
  (v: string) => !!v || '이름을 입력해주세요',
  (v: string) => v.length >= 2 || '이름은 최소 2자 이상이어야 합니다'
]

const emailRules = [
  (v: string) => !!v || '이메일을 입력해주세요',
  (v: string) => /.+@.+\..+/.test(v) || '올바른 이메일 형식을 입력해주세요'
]

const passwordRules = [
  (v: string) => !!v || '비밀번호를 입력해주세요',
  (v: string) => v.length >= 6 || '비밀번호는 최소 6자 이상이어야 합니다'
]

const confirmPasswordRules = [
  (v: string) => !!v || '비밀번호 확인을 입력해주세요',
  (v: string) => v === password.value || '비밀번호가 일치하지 않습니다'
]

const handleRegister = async () => {
  if (!isFormValid.value) return
  
  isLoading.value = true
  try {
    // TODO: 회원가입 로직 구현
    console.log('회원가입 시도:', { 
      name: name.value, 
      email: email.value, 
      password: password.value 
    })
    await new Promise(resolve => setTimeout(resolve, 1000)) // 임시 딜레이
  } catch (error) {
    console.error('회원가입 실패:', error)
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
