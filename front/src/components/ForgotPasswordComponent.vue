<template>
  <v-card
    class="forgot-card mx-auto"
    max-width="580"
    elevation="12"
    rounded="xl"
  >
    <v-card-title class="text-center pa-8 pb-4">
      <h2 class="forgot-title">비밀번호 찾기</h2>
      <p class="forgot-subtitle mt-2">이메일로 재설정 링크를 받으세요</p>
    </v-card-title>
    
    <v-card-text class="px-8 pb-8">
      <div v-if="!emailSent">
        <p class="text-body-2 text-grey-darken-1 mb-6 text-center">
          가입하신 이메일 주소를 입력해주세요.<br>
          비밀번호 재설정 링크를 보내드립니다.
        </p>
        
        <v-form @submit.prevent="handleForgotPassword">
          <v-text-field
            v-model="email"
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
          
          <v-btn
            type="submit"
            color="#00C851"
            variant="flat"
            size="x-large"
            block
            class="forgot-btn mb-6"
            :loading="loading"
            rounded="lg"
            height="56"
          >
            재설정 링크 보내기
          </v-btn>
          
          <div class="text-center">
            <v-btn
              variant="text"
              color="#666"
              size="small"
              @click="$emit('switchTo', 'login')"
              class="back-btn"
            >
              ← 로그인으로 돌아가기
            </v-btn>
          </div>
        </v-form>
      </div>
      
      <!-- 이메일 전송 완료 상태 -->
      <div v-else class="text-center">
        <div class="success-icon mb-6">
          <v-icon
            icon="mdi-email-check"
            size="80"
            color="#00C851"
          ></v-icon>
        </div>
        
        <h3 class="success-title mb-4">이메일이 전송되었습니다!</h3>
        
        <p class="success-message mb-6">
          <strong>{{ email }}</strong>로<br>
          비밀번호 재설정 링크를 보내드렸습니다.<br>
          이메일을 확인해주세요.
        </p>
        
        <v-btn
          color="#00C851"
          variant="outlined"
          size="large"
          block
          class="mb-6 resend-btn"
          @click="resendEmail"
          :loading="resendLoading"
          rounded="lg"
        >
          다시 보내기
        </v-btn>
        
        <div class="text-center">
          <v-btn
            variant="text"
            color="#666"
            size="small"
            @click="$emit('switchTo', 'login')"
            class="back-btn"
          >
            ← 로그인으로 돌아가기
          </v-btn>
        </div>
      </div>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { ref } from 'vue'

// Props & Emits
defineEmits(['switchTo'])

// Reactive data
const email = ref('')
const emailSent = ref(false)
const loading = ref(false)
const resendLoading = ref(false)

// Validation rules
const emailRules = [
  (v: string) => !!v || '이메일을 입력해주세요',
  (v: string) => /.+@.+\..+/.test(v) || '올바른 이메일 형식이 아닙니다'
]

// Methods
const handleForgotPassword = async () => {
  loading.value = true
  
  try {
    // 여기에 비밀번호 재설정 API 호출 로직 추가
    console.log('비밀번호 재설정 시도:', email.value)
    
    // 임시로 2초 대기
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // 성공 처리
    emailSent.value = true
    
  } catch (error) {
    console.error('비밀번호 재설정 오류:', error)
    alert('비밀번호 재설정에 실패했습니다.')
  } finally {
    loading.value = false
  }
}

const resendEmail = async () => {
  resendLoading.value = true
  
  try {
    // 여기에 재전송 API 호출 로직 추가
    console.log('이메일 재전송:', email.value)
    
    // 임시로 1초 대기
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 성공 처리
    alert('이메일을 다시 보냈습니다.')
    
  } catch (error) {
    console.error('이메일 재전송 오류:', error)
    alert('이메일 재전송에 실패했습니다.')
  } finally {
    resendLoading.value = false
  }
}
</script>

<style scoped>
.forgot-card {
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1), 0 0 0 1px rgba(255, 255, 255, 0.1);
}

.forgot-title {
  color: #2c3e50;
  font-weight: 700;
  font-size: 2rem;
  margin: 0;
}

.forgot-subtitle {
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

.forgot-btn {
  font-weight: 700 !important;
  text-transform: none !important;
  font-size: 1.1rem !important;
  box-shadow: 0 8px 20px rgba(0, 200, 81, 0.3);
  transition: all 0.3s ease;
  background: linear-gradient(135deg, #00C851 0%, #00E676 100%);
}

.forgot-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 25px rgba(0, 200, 81, 0.4);
}

.forgot-btn:active {
  transform: translateY(0);
}

.success-icon {
  animation: bounceIn 0.6s ease-out;
}

.success-title {
  color: #00C851;
  font-weight: 700;
  font-size: 1.5rem;
  margin: 0;
}

.success-message {
  color: #7f8c8d;
  font-size: 1rem;
  line-height: 1.6;
  margin: 0;
}

.resend-btn {
  font-weight: 600 !important;
  text-transform: none !important;
  border-width: 2px !important;
  transition: all 0.3s ease;
}

.resend-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 200, 81, 0.2);
}

.back-btn {
  text-transform: none !important;
  font-size: 0.9rem !important;
  font-weight: 500;
  transition: all 0.3s ease;
}

.back-btn:hover {
  color: #00C851 !important;
  transform: translateY(-1px);
}

/* 애니메이션 */
@keyframes bounceIn {
  0% {
    opacity: 0;
    transform: scale(0.3);
  }
  50% {
    opacity: 1;
    transform: scale(1.05);
  }
  70% {
    transform: scale(0.9);
  }
  100% {
    opacity: 1;
    transform: scale(1);
  }
}

/* 반응형 디자인 */
@media (max-width: 600px) {
  .forgot-card {
    max-width: 100%;
    margin: 0 16px;
  }
  
  .forgot-title {
    font-size: 1.75rem;
  }
  
  .forgot-subtitle {
    font-size: 0.9rem;
  }
  
  .success-title {
    font-size: 1.25rem;
  }
}
</style>
