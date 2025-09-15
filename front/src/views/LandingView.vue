<template>
  <div class="landing-container">
    <!-- 헤더 컴포넌트 -->
    <HeaderComponent />
    
    <!-- 메인 콘텐츠 -->
    <div class="main-content">
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
            <div v-if="!showForm && !userStore.isLoggedIn" class="action-buttons mt-4">
              <button
                class="btn btn-basic"
                @click="showLoginForm"
              >
                로그인
              </button>
              <button
                class="btn btn-basic02"
                @click="showRegisterForm"
              >
                회원가입
              </button>
            </div>
          </div>
        </div>
        
        <!-- 오른쪽: 폼 영역 -->
        <div v-if="showForm && !userStore.isLoggedIn" class="form-section">
          <component 
            :is="currentForm" 
            @switchForm="switchForm"
            @loginSuccess="showForm = false"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import HeaderComponent from '@/components/HeaderComponent.vue'
import LoginComponent from '@/components/LoginComponent.vue'
import RegisterComponent from '@/components/RegisterComponent.vue'
import ForgotPasswordComponent from '@/components/ForgotPasswordComponent.vue'
import "../assets/styles/btn.css"
import { useUserStore } from '@/stores/user'



const showForm = ref(false)
const currentFormType = ref('login')
const userStore = useUserStore()

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
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
  background: linear-gradient(135deg, #E3F2FD 0%, #F1F8E9 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.content-wrapper {
  max-width: 1200px;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  gap: 4rem;
  padding: 0 2rem;
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
  margin-bottom: 1.2rem;
  color: #1a1a1a;
}

.highlight {
  color: #1976d2;
}

.welcome-subtitle {
  font-size: 1.25rem;
  line-height: 1.6;
  color: #666;
}

.action-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 0.8rem;
}

.btn-login,
.btn-register {
  padding: 0.8rem 1.6rem;
  border-radius: 0.4rem;
  font-weight: 600;
  font-size: 1.1rem;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
}

.btn-login {
  background-color: #1976d2;
  color: white;
}

.btn-login:hover {
  background-color: #1565c0;
}

.btn-register {
  background-color: transparent;
  border: 0.1rem solid #1976d2;
  color: #1976d2;
}

.btn-register:hover {
  background-color: #1976d2;
  color: white;
}

.form-section {
  flex: 0 0 450px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
