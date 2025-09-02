<template>
  <v-card
    class="login-card mx-auto"
    max-width="580"
    elevation="12"
    rounded="xl"
  >
    <v-card-title class="text-center pa-8 pb-4">
      <h2 class="login-title">로그인</h2>
      <p class="login-subtitle mt-2">계정에 로그인하세요</p>
    </v-card-title>
    
    <v-card-text class="px-8 pb-8">
      <v-form @submit.prevent="handleLogin">
        <v-text-field
          v-model="loginForm.email"
          label="이메일"
          type="email"
          variant="outlined"
          prepend-inner-icon="mdi-email"
          class="mb-6 custom-input"
          :rules="emailRules"
          required
          bg-color="grey-lighten-5"
          rounded="lg"
        ></v-text-field>
        
        <v-text-field
          v-model="loginForm.password"
          label="비밀번호"
          :type="showPassword ? 'text' : 'password'"
          variant="outlined"
          prepend-inner-icon="mdi-lock"
          :append-inner-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
          @click:append-inner="showPassword = !showPassword"
          class="mb-6 custom-input"
          :rules="passwordRules"
          required
          bg-color="grey-lighten-5"
          rounded="lg"
        ></v-text-field>
        
        <v-btn
          type="submit"
          color="#00C851"
          variant="flat"
          size="x-large"
          block
          class="login-btn mb-6"
          :loading="loading"
          rounded="lg"
          height="56"
        >
          로그인
        </v-btn>
        
        <div class="text-center mb-6">
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
            class="ml-2 register-link"
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
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1), 0 0 0 1px rgba(255, 255, 255, 0.1);
}

.login-title {
  color: #2c3e50;
  font-weight: 700;
  font-size: 2rem;
  margin: 0;
}

.login-subtitle {
  color: #7f8c8d;
  font-size: 1rem;
  font-weight: 400;
  margin: 0;
}

.custom-input {
  font-size: 1rem;
}

.custom-input :deep(.v-field) {
  border-radius: 12px;
  transition: all 0.3s ease;
}

.custom-input :deep(.v-field:hover) {
  background-color: #f5f5f5;
  transform: translateY(-1px);
}

.custom-input :deep(.v-field--focused) {
  background-color: #ffffff;
  box-shadow: 0 4px 12px rgba(0, 200, 81, 0.15);
}

.login-btn {
  font-weight: 700 !important;
  text-transform: none !important;
  font-size: 1.1rem !important;
  box-shadow: 0 8px 20px rgba(0, 200, 81, 0.3);
  transition: all 0.3s ease;
  background: linear-gradient(135deg, #00C851 0%, #00E676 100%);
}

.login-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 25px rgba(0, 200, 81, 0.4);
}

.login-btn:active {
  transform: translateY(0);
}

.forgot-btn {
  text-transform: none !important;
  font-size: 0.9rem !important;
  font-weight: 500;
  transition: all 0.3s ease;
}

.forgot-btn:hover {
  color: #00C851 !important;
  transform: translateY(-1px);
}

.register-link {
  text-transform: none !important;
  font-weight: 600;
  transition: all 0.3s ease;
}

.register-link:hover {
  transform: translateY(-1px);
  text-decoration: underline;
}

/* 반응형 디자인 */
@media (max-width: 600px) {
  .login-card {
    max-width: 100%;
    margin: 0 16px;
  }
  
  .login-title {
    font-size: 1.75rem;
  }
  
  .login-subtitle {
    font-size: 0.9rem;
  }
}
</style>
