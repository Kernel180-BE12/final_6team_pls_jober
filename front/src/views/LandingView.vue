<template>
  <div class="landing-container">
    <!-- 메인 콘텐츠 -->
    <div class="main-content">
      <v-container class="h-100 pa-0">
        <div class="content-wrapper">
          <!-- 왼쪽: 환영 메시지 -->
          <div class="welcome-section" :class="{ 'moved-left': showForm }">
            <div class="welcome-content">
              <h1 class="welcome-title">
                AI 템플릿으로<br>
                <span class="highlight">창의적인 작업</span>을<br>
                시작하세요
              </h1>
              <p class="welcome-subtitle">
                인공지능이 도와주는 템플릿으로<br>
                더욱 효율적이고 창의적인 작업을 경험해보세요
              </p>
              
              <!-- 초기 상태: 로그인/회원가입 버튼 -->
              <div v-if="!showForm" class="action-buttons">
                <v-btn
                  color="primary"
                  size="x-large"
                  variant="elevated"
                  @click="showLoginForm"
                  class="mr-4 mb-2"
                >
                  로그인
                </v-btn>
                <v-btn
                  color="secondary"
                  size="x-large"
                  variant="outlined"
                  @click="showRegisterForm"
                  class="mb-2"
                >
                  회원가입
                </v-btn>
              </div>
            </div>
          </div>
          
          <!-- 오른쪽: 폼 영역 -->
          <div v-if="showForm" class="form-section">
            <component 
              :is="currentForm" 
              @switchForm="switchForm"
            />
          </div>
        </div>
      </v-container>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import LoginComponent from '@/components/LoginComponent.vue'
import RegisterComponent from '@/components/RegisterComponent.vue'
import ForgotPasswordComponent from '@/components/ForgotPasswordComponent.vue'

const showForm = ref(false)
const currentFormType = ref('login')

const currentForm = computed(() => {
  switch (currentFormType.value) {
    case 'login':
      return LoginComponent
    case 'register':
      return RegisterComponent
    case 'forgot':
      return ForgotPasswordComponent
    default:
      return LoginComponent
  }
})

const showLoginForm = () => {
  currentFormType.value = 'login'
  showForm.value = true
}

const showRegisterForm = () => {
  currentFormType.value = 'register'
  showForm.value = true
}

const switchForm = (formType: string) => {
  currentFormType.value = formType
}
</script>

<style scoped>
.landing-container {
  height: calc(100vh - 64px); /* 헤더 높이 제외 */
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
  display: flex;
  align-items: center;
  min-height: 0;
}

.content-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  gap: 80px;
  padding: 0 40px;
}

.welcome-section {
  flex: 1;
  max-width: 600px;
  transition: all 0.5s ease;
}

.welcome-section.moved-left {
  flex: 0 0 500px;
  max-width: 500px;
}

.welcome-content {
  text-align: left;
}

.welcome-title {
  font-size: 3.5rem;
  font-weight: 700;
  line-height: 1.2;
  margin-bottom: 24px;
  color: #1a1a1a;
}

.highlight {
  color: #1976d2;
}

.welcome-subtitle {
  font-size: 1.25rem;
  line-height: 1.6;
  color: #666;
  margin-bottom: 48px;
}

.action-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.form-section {
  flex: 0 0 450px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 반응형 디자인 제거 - 고정 레이아웃 */
@media (max-width: 1200px) {
  .content-wrapper {
    gap: 60px;
    padding: 0 30px;
  }
  
  .welcome-title {
    font-size: 3rem;
  }
}

@media (max-width: 900px) {
  .content-wrapper {
    flex-direction: column;
    gap: 40px;
    padding: 0 20px;
  }
  
  .welcome-section,
  .welcome-section.moved-left {
    flex: none;
    max-width: 100%;
    text-align: center;
  }
  
  .welcome-content {
    text-align: center;
  }
  
  .form-section {
    flex: none;
    width: 100%;
    max-width: 450px;
  }
}
</style>
