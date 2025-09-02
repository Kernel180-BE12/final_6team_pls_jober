<template>
  <v-card
    class="register-card mx-auto"
    max-width="400"
    elevation="8"
    rounded="lg"
  >
    <v-card-title class="text-center pa-6">
      <h2 class="register-title">회원가입</h2>
    </v-card-title>
    
    <v-card-text class="px-6 pb-6">
      <v-form @submit.prevent="handleRegister">
        <v-text-field
          v-model="registerForm.name"
          label="이름"
          variant="outlined"
          prepend-inner-icon="mdi-account"
          class="mb-4"
          :rules="nameRules"
          required
        ></v-text-field>
        
        <v-text-field
          v-model="registerForm.email"
          label="이메일"
          type="email"
          variant="outlined"
          prepend-inner-icon="mdi-email"
          class="mb-4"
          :rules="emailRules"
          required
        ></v-text-field>
        
        <v-text-field
          v-model="registerForm.password"
          label="비밀번호"
          :type="showPassword ? 'text' : 'password'"
          variant="outlined"
          prepend-inner-icon="mdi-lock"
          :append-inner-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
          @click:append-inner="showPassword = !showPassword"
          class="mb-4"
          :rules="passwordRules"
          required
        ></v-text-field>
        
        <v-text-field
          v-model="registerForm.confirmPassword"
          label="비밀번호 확인"
          :type="showConfirmPassword ? 'text' : 'password'"
          variant="outlined"
          prepend-inner-icon="mdi-lock-check"
          :append-inner-icon="showConfirmPassword ? 'mdi-eye' : 'mdi-eye-off'"
          @click:append-inner="showConfirmPassword = !showConfirmPassword"
          class="mb-4"
          :rules="confirmPasswordRules"
          required
        ></v-text-field>
        
        <v-text-field
          v-model="registerForm.phone"
          label="전화번호"
          variant="outlined"
          prepend-inner-icon="mdi-phone"
          class="mb-6"
          :rules="phoneRules"
          placeholder="010-1234-5678"
          required
        ></v-text-field>
        
        <v-btn
          type="submit"
          color="#00C851"
          variant="flat"
          size="large"
          block
          class="register-btn mb-4"
          :loading="loading"
        >
          회원가입
        </v-btn>
        
        <v-divider class="my-6"></v-divider>
        
        <div class="text-center">
          <span class="text-body-2 text-grey-darken-1">이미 계정이 있으신가요?</span>
          <v-btn
            variant="text"
            color="#00C851"
            size="small"
            @click="$emit('switchTo', 'login')"
            class="ml-2"
          >
            로그인
          </v-btn>
        </div>
      </v-form>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'

// Props & Emits
defineEmits(['switchTo'])

// Reactive data
const showPassword = ref(false)
const showConfirmPassword = ref(false)
const loading = ref(false)
const registerForm = reactive({
  name: '',
  email: '',
  password: '',
  confirmPassword: '',
  phone: ''
})

// Validation rules
const nameRules = [
  (v: string) => !!v || '이름을 입력해주세요',
  (v: string) => v.length >= 2 || '이름은 2자 이상이어야 합니다'
]

const emailRules = [
  (v: string) => !!v || '이메일을 입력해주세요',
  (v: string) => /.+@.+\..+/.test(v) || '올바른 이메일 형식이 아닙니다'
]

const passwordRules = [
  (v: string) => !!v || '비밀번호를 입력해주세요',
  (v: string) => v.length >= 8 || '비밀번호는 8자 이상이어야 합니다',
  (v: string) => /(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(v) || '영문 대소문자와 숫자를 포함해야 합니다'
]

const confirmPasswordRules = [
  (v: string) => !!v || '비밀번호 확인을 입력해주세요',
  (v: string) => v === registerForm.password || '비밀번호가 일치하지 않습니다'
]

const phoneRules = [
  (v: string) => !!v || '전화번호를 입력해주세요',
  (v: string) => /^010-\d{4}-\d{4}$/.test(v) || '올바른 전화번호 형식이 아닙니다 (010-1234-5678)'
]

// Methods
const handleRegister = async () => {
  loading.value = true
  
  try {
    // 여기에 회원가입 API 호출 로직 추가
    console.log('회원가입 시도:', registerForm)
    
    // 임시로 2초 대기
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // 성공 처리
    alert('회원가입 성공!')
    
  } catch (error) {
    console.error('회원가입 오류:', error)
    alert('회원가입에 실패했습니다.')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
}

.register-title {
  color: #333;
  font-weight: 600;
}

.register-btn {
  font-weight: 600 !important;
  text-transform: none !important;
  box-shadow: 0 2px 8px rgba(0, 200, 81, 0.3);
  transition: all 0.3s ease;
}

.register-btn:hover {
  box-shadow: 0 4px 12px rgba(0, 200, 81, 0.4);
  transform: translateY(-1px);
}
</style>
