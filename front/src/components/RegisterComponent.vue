<template>
  <v-card
    class="register-card mx-auto"
    max-width="580"
    elevation="12"
    rounded="xl"
  >
    <v-card-title class="text-center pa-8 pb-4">
      <h2 class="register-title">회원가입</h2>
      <p class="register-subtitle mt-2">새로운 계정을 만들어보세요</p>
    </v-card-title>
    
    <v-card-text class="px-8 pb-8">
      <v-form @submit.prevent="handleRegister">
        <v-text-field
          v-model="registerForm.name"
          label="이름"
          variant="outlined"
          prepend-inner-icon="mdi-account"
          class="mb-5 custom-input"
          :rules="nameRules"
          required
          bg-color="grey-lighten-5"
          rounded="lg"
        ></v-text-field>
        
        <v-text-field
          v-model="registerForm.email"
          label="이메일"
          type="email"
          variant="outlined"
          prepend-inner-icon="mdi-email"
          class="mb-5 custom-input"
          :rules="emailRules"
          required
          bg-color="grey-lighten-5"
          rounded="lg"
        ></v-text-field>
        
        <v-text-field
          v-model="registerForm.password"
          label="비밀번호"
          :type="showPassword ? 'text' : 'password'"
          variant="outlined"
          prepend-inner-icon="mdi-lock"
          :append-inner-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
          @click:append-inner="showPassword = !showPassword"
          class="mb-5 custom-input"
          :rules="passwordRules"
          required
          bg-color="grey-lighten-5"
          rounded="lg"
        ></v-text-field>
        
        <v-text-field
          v-model="registerForm.confirmPassword"
          label="비밀번호 확인"
          :type="showConfirmPassword ? 'text' : 'password'"
          variant="outlined"
          prepend-inner-icon="mdi-lock-check"
          :append-inner-icon="showConfirmPassword ? 'mdi-eye' : 'mdi-eye-off'"
          @click:append-inner="showConfirmPassword = !showConfirmPassword"
          class="mb-5 custom-input"
          :rules="confirmPasswordRules"
          required
          bg-color="grey-lighten-5"
          rounded="lg"
        ></v-text-field>
        
        <v-text-field
          v-model="registerForm.phone"
          label="전화번호"
          variant="outlined"
          prepend-inner-icon="mdi-phone"
          class="mb-6 custom-input"
          :rules="phoneRules"
          placeholder="010-1234-5678"
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
          class="register-btn mb-6"
          :loading="loading"
          rounded="lg"
          height="56"
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
            class="ml-2 login-link"
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
  (v: string) => v.length >= 6 || '비밀번호는 6자 이상이어야 합니다'
]

const confirmPasswordRules = [
  (v: string) => !!v || '비밀번호 확인을 입력해주세요',
  (v: string) => v === registerForm.password || '비밀번호가 일치하지 않습니다'
]

const phoneRules = [
  (v: string) => !!v || '전화번호를 입력해주세요',
  (v: string) => /^[0-9-]+$/.test(v) || '올바른 전화번호 형식이 아닙니다'
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
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1), 0 0 0 1px rgba(255, 255, 255, 0.1);
}

.register-title {
  color: #2c3e50;
  font-weight: 700;
  font-size: 2rem;
  margin: 0;
}

.register-subtitle {
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

.register-btn {
  font-weight: 700 !important;
  text-transform: none !important;
  font-size: 1.1rem !important;
  box-shadow: 0 8px 20px rgba(0, 200, 81, 0.3);
  transition: all 0.3s ease;
  background: linear-gradient(135deg, #00C851 0%, #00E676 100%);
}

.register-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 25px rgba(0, 200, 81, 0.4);
}

.register-btn:active {
  transform: translateY(0);
}

.login-link {
  text-transform: none !important;
  font-weight: 600;
  transition: all 0.3s ease;
}

.login-link:hover {
  transform: translateY(-1px);
  text-decoration: underline;
}

/* 반응형 디자인 */
@media (max-width: 600px) {
  .register-card {
    max-width: 100%;
    margin: 0 16px;
  }
  
  .register-title {
    font-size: 1.75rem;
  }
  
  .register-subtitle {
    font-size: 0.9rem;
  }
}
</style>
