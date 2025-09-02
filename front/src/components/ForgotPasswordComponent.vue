<template>
  <v-card
    class="forgot-card mx-auto"
    max-width="400"
    elevation="8"
    rounded="lg"
  >
    <v-card-title class="text-center pa-6">
      <h2 class="forgot-title">비밀번호 찾기</h2>
    </v-card-title>
    
    <v-card-text class="px-6 pb-6">
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
            class="mb-6"
            :rules="emailRules"
            required
          ></v-text-field>
          
          <v-btn
            type="submit"
            color="#00C851"
            variant="flat"
            size="large"
            block
            class="forgot-btn mb-4"
            :loading="loading"
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
        <v-icon
          icon="mdi-email-check"
          size="64"
          color="#00C851"
          class="mb-4"
        ></v-icon>
        
        <h3 class="mb-4 text-success">이메일이 전송되었습니다!</h3>
        
        <p class="text-body-2 text-grey-darken-1 mb-6">
          <strong>{{ email }}</strong>로<br>
          비밀번호 재설정 링크를 보내드렸습니다.<br>
          이메일을 확인해주세요.
        </p>
        
        <v-btn
          color="#00C851"
          variant="outlined"
          size="large"
          block
          class="mb-4"
          @click="resendEmail"
          :loading="resendLoading"
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
const loading = ref(false)
const resendLoading = ref(false)
const emailSent = ref(false)

// Validation rules
const emailRules = [
  (v: string) => !!v || '이메일을 입력해주세요',
  (v: string) => /.+@.+\..+/.test(v) || '올바른 이메일 형식이 아닙니다'
]

// Methods
const handleForgotPassword = async () => {
  loading.value = true
  
  try {
    // 여기에 비밀번호 재설정 이메일 전송 API 호출 로직 추가
    console.log('비밀번호 재설정 이메일 전송:', email.value)
    
    // 임시로 2초 대기
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // 성공 처리
    emailSent.value = true
    
  } catch (error) {
    console.error('이메일 전송 오류:', error)
    alert('이메일 전송에 실패했습니다.')
  } finally {
    loading.value = false
  }
}

const resendEmail = async () => {
  resendLoading.value = true
  
  try {
    // 재전송 로직
    await new Promise(resolve => setTimeout(resolve, 1000))
    alert('이메일이 다시 전송되었습니다.')
    
  } catch (error) {
    console.error('재전송 오류:', error)
    alert('재전송에 실패했습니다.')
  } finally {
    resendLoading.value = false
  }
}
</script>

<style scoped>
.forgot-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
}

.forgot-title {
  color: #333;
  font-weight: 600;
}

.forgot-btn {
  font-weight: 600 !important;
  text-transform: none !important;
  box-shadow: 0 2px 8px rgba(0, 200, 81, 0.3);
  transition: all 0.3s ease;
}

.forgot-btn:hover {
  box-shadow: 0 4px 12px rgba(0, 200, 81, 0.4);
  transform: translateY(-1px);
}

.back-btn {
  text-transform: none !important;
  font-size: 12px !important;
}
</style>
