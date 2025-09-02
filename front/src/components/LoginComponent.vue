<template>
  <v-card
    class="login-card mx-auto"
    max-width="400"
    elevation="8"
    rounded="lg"
  >
    <v-card-title class="text-center pa-6">
      <h2 class="login-title">로그인</h2>
    </v-card-title>
    
    <v-card-text class="px-6 pb-6">
      <v-form @submit.prevent="handleLogin">
        <v-text-field
          v-model="loginForm.email"
          label="이메일"
          type="email"
          variant="outlined"
          prepend-inner-icon="mdi-email"
          class="mb-4"
          :rules="emailRules"
          required
        ></v-text-field>
        
        <v-text-field
          v-model="loginForm.password"
          label="비밀번호"
          :type="showPassword ? 'text' : 'password'"
          variant="outlined"
          prepend-inner-icon="mdi-lock"
          :append-inner-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
          @click:append-inner="showPassword = !showPassword"
          class="mb-6"
          :rules="passwordRules"
          required
        ></v-text-field>
        
        <v-btn
          type="submit"
          color="#00C851"
          variant="flat"
          size="large"
          block
          class="login-btn mb-4"
          :loading="loading"
        >
          로그인
        </v-btn>
        
        <div class="text-center">
          <v-btn
            variant="text"
            color="#666"
            size="small"
            @click="$emit('switchTo', 'forgot')"
            class="forgot-btn"
          >
            비밀번호를 잊으셨나요?
          </v-btn>
        </div>
        
        <v-divider class="my-6"></v-divider>
        
        <div class="text-center">
          <span class="text-body-2 text-grey-darken-1">아직 계정이 없으신가요?</span>
          <v-btn
            variant="text"
            color="#00C851"
            size="small"
            @click="$emit('switchTo', 'register')"
            class="ml-2"
          >
            회원가입
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
const loading = ref(false)
const loginForm = reactive({
  email: '',
  password: ''
})

// Validation rules
const emailRules = [
  (v: string) => !!v || '이메일을 입력해주세요',
  (v: string) => /.+@.+\..+/.test(v) || '올바른 이메일 형식이 아닙니다'
]

const passwordRules = [
  (v: string) => !!v || '비밀번호를 입력해주세요',
  (v: string) => v.length >= 6 || '비밀번호는 6자 이상이어야 합니다'
]

// Methods
const handleLogin = async () => {
  loading.value = true
  
  try {
    // 여기에 로그인 API 호출 로직 추가
    console.log('로그인 시도:', loginForm)
    
    // 임시로 2초 대기
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // 성공 처리
    alert('로그인 성공!')
    
  } catch (error) {
    console.error('로그인 오류:', error)
    alert('로그인에 실패했습니다.')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
}

.login-title {
  color: #333;
  font-weight: 600;
}

.login-btn {
  font-weight: 600 !important;
  text-transform: none !important;
  box-shadow: 0 2px 8px rgba(0, 200, 81, 0.3);
  transition: all 0.3s ease;
}

.login-btn:hover {
  box-shadow: 0 4px 12px rgba(0, 200, 81, 0.4);
  transform: translateY(-1px);
}

.forgot-btn {
  text-transform: none !important;
  font-size: 12px !important;
}
</style>
