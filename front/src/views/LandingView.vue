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
            <div v-if="!userStore.isLoggedIn" class="action-buttons mt-4">
              <div class="auth-buttons">
                <button
                  class="btn-auth btn-login"
                  @click="openLoginForm"
                >
                  로그인
                </button>
                <button
                  class="btn-auth btn-register"
                  @click="openRegisterForm"
                >
                  회원가입
                </button>
              </div>
              <div class="divider">
                <span>또는</span>
              </div>
              <button
                class="btn-kakao"
                @click="handleKakaoLogin"
                :disabled="isKakaoLoading"
              >
                <span v-if="isKakaoLoading">
                  <i class="mdi mdi-loading mdi-spin"></i>
                  로딩중...
                </span>
                <span v-else>
                  <i class="mdi mdi-chat"></i>
                  카카오로 시작하기
                </span>
              </button>
            </div>
          </div>
        </div>
        
        <!-- 오른쪽: 폼 영역 -->
        <div class="form-section" v-if="userStore.isLoggedIn || showLoginForm">
          <!-- 로그인된 상태에서만 템플릿 생성 모달 표시 -->
          <TemplateCreateComponent
            v-if="userStore.isLoggedIn && !showLoginForm"
            @requireLogin="showLoginForm = true"
          />
          
          <!-- 로그인/회원가입/비번찾기 폼 -->
          <component
            v-else-if="showLoginForm"
            :is="currentForm"
            @switchForm="switchForm"
            @loginSuccess="handleLoginSuccess"
          />
        </div>
      </div>
    </div>
  </div>
</template> 

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import HeaderComponent from '@/components/HeaderComponent.vue'
import LoginComponent from '@/components/LoginComponent.vue'
import RegisterComponent from '@/components/RegisterComponent.vue'
import ForgotPasswordComponent from '@/components/ForgotPasswordComponent.vue'
import TemplateCreateComponent from '@/components/TemplateCreateComponent.vue'
import "../assets/styles/btn.css"
import { useUserStore } from '@/stores/user'
import { authApi } from '@/api'

const userStore = useUserStore()
const route = useRoute()
const router = useRouter()

// 상태
const showLoginForm = ref(false)
const currentFormType = ref('login')
const showForm = ref(false) // welcome-section 애니메이션용
const isKakaoLoading = ref(false)

// 현재 표시할 폼 계산
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

// 로그인/회원가입 버튼 눌렀을 때
const openLoginForm = () => {
  currentFormType.value = 'login'
  showForm.value = true
  showLoginForm.value = true
}

const openRegisterForm = () => {
  currentFormType.value = 'register'
  showForm.value = true
  showLoginForm.value = true
}

const switchForm = (formType: string) => {
  currentFormType.value = formType
}

// 로그인 성공 시 처리
const handleLoginSuccess = () => {
  showLoginForm.value = false
  showForm.value = false
}

// 카카오 로그인 처리
const handleKakaoLogin = async () => {
  isKakaoLoading.value = true

  try {
    // 백엔드에서 카카오 로그인 URL 가져오기
    const response = await authApi.getKakaoLoginUrl()

    // 카카오 로그인 페이지로 리다이렉트
    window.location.href = response.data.url
  } catch (error: any) {
    console.error('카카오 로그인 실패:', error)
    alert('카카오 로그인에 실패했습니다.')
  } finally {
    isKakaoLoading.value = false
  }
}

// 카카오 로그인/로그아웃 콜백 처리
onMounted(() => {
  const urlParams = new URLSearchParams(window.location.search)
  const accessToken = urlParams.get('accessToken')
  const refreshToken = urlParams.get('refreshToken')
  const userId = urlParams.get('userId')
  const role = urlParams.get('role')
  const error = urlParams.get('error')
  const logout = urlParams.get('logout')

  // 카카오 로그아웃 콜백 처리
  if (logout === 'success') {
    console.log('카카오 로그아웃 완료')
    // URL 파라미터 제거
    router.replace({ path: '/' })
    return
  }

  if (error) {
    console.error('카카오 로그인 에러:', error)
    alert('카카오 로그인에 실패했습니다: ' + error)
    // URL 파라미터 제거
    router.replace({ path: '/' })
    return
  }

  if (accessToken && refreshToken && userId && role) {
    console.log('카카오 로그인 성공, 토큰 저장 중...')

    // 유저 스토어에 토큰과 사용자 정보 저장 (카카오 로그인)
    userStore.setUser(
      {
        accountId: parseInt(userId),
        role: role
      },
      {
        accessToken: accessToken,
        refreshToken: refreshToken
      },
      'kakao' // 카카오 로그인 타입 설정
    )

    // URL 파라미터 제거하고 랜딩 페이지로 이동
    router.replace({ path: '/' })

    // 로그인 폼 닫기
    handleLoginSuccess()
  }
})
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
  flex-direction: column;
  gap: 0.5rem;
  width: 100%;
  max-width: 400px;
  margin-top: 2rem;
}

.auth-buttons {
  display: flex;
  gap: 0.75rem;
}

.btn-auth {
  flex: 1;
  padding: 0.7rem 1.2rem;
  border-radius: 0.5rem;
  font-weight: 500;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 44px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.btn-auth:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.btn-login {
  background-color: #1976d2;
  color: white;
}

.btn-login:hover {
  background-color: #1565c0;
}

.btn-register {
  background-color: white;
  border: 1px solid #e0e0e0;
  color: #424242;
}

.btn-register:hover {
  background-color: #f5f5f5;
  border-color: #1976d2;
  color: #1976d2;
}

.divider {
  display: flex;
  align-items: center;
  text-align: center;
  margin: 0.5rem 0;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: #e0e0e0;
}

.divider span {
  padding: 0 1rem;
  color: #999;
  font-size: 0.9rem;
  background: linear-gradient(135deg, #E3F2FD 0%, #F1F8E9 100%);
}

.btn-kakao {
  width: 100%;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-weight: 500;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  min-height: 44px;
  background-color: #FEE500;
  color: #3c1e1e;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.btn-kakao:hover:not(:disabled) {
  background-color: #fdd835;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.btn-kakao:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.btn-kakao i {
  font-size: 1.1rem;
}

.mdi-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.form-section {
  flex: 0 0 450px;
  display: flex;
  align-items: center;
  justify-content: center;
}

</style>
