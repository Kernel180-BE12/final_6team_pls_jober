<template>
  <div class="landing-page">
    <!-- 헤더 -->
    <HeaderComponent />
    
    <!-- 메인 콘텐츠 -->
    <v-main class="main-content">
      <v-container fluid class="pa-0">
        <!-- 히어로 섹션 -->
        <section class="hero-section">
          <v-container class="hero-container">
            <v-row justify="center" align="center" class="min-height-screen">
              <v-col cols="12" md="6" class="text-center">
                <div class="hero-content">
                  <h1 class="hero-title mb-4">
                    메시지 생성부터 발송까지
                  </h1>
                  <p class="hero-subtitle mb-8">
                    메시징 AI 에이전트, 자버
                  </p>
                  
                  <div class="hero-buttons mb-8">
                    <v-btn
                      color="#333"
                      variant="outlined"
                      size="x-large"
                      class="mr-4 hero-btn"
                      rounded="pill"
                      @click="currentView = 'register'"
                    >
                      상담 신청
                    </v-btn>
                    
                    <v-btn
                      color="#00C851"
                      variant="flat"
                      size="x-large"
                      class="hero-btn"
                      rounded="pill"
                      @click="showAuthModal = true"
                    >
                      무료로 발송하기 →
                    </v-btn>
                  </div>
                </div>
              </v-col>
              
              <v-col cols="12" md="6" class="text-center">
                <div class="auth-section">
                  <!-- 인증 폼들 -->
                  <transition name="fade" mode="out-in">
                    <LoginComponent 
                      v-if="currentView === 'login'"
                      @switchTo="switchView"
                    />
                    <RegisterComponent 
                      v-else-if="currentView === 'register'"
                      @switchTo="switchView"
                    />
                    <ForgotPasswordComponent 
                      v-else-if="currentView === 'forgot'"
                      @switchTo="switchView"
                    />
                  </transition>
                </div>
              </v-col>
            </v-row>
          </v-container>
        </section>
        
        <!-- 하단 문의 섹션 -->
        <section class="inquiry-section">
          <v-container>
            <v-row justify="center">
              <v-col cols="12" class="text-center">
                <div class="inquiry-content">
                  <h3 class="inquiry-title mb-4">무엇을 발송할 수 있나요?</h3>
                  
                  <!-- 채팅 아이콘 -->
                  <div class="chat-icon">
                    <v-avatar size="60" color="#333">
                      <v-icon icon="mdi-chat" size="30" color="white"></v-icon>
                    </v-avatar>
                  </div>
                </div>
              </v-col>
            </v-row>
          </v-container>
        </section>
      </v-container>
    </v-main>
    
    <!-- 모달 (필요시) -->
    <v-dialog v-model="showAuthModal" max-width="500">
      <LoginComponent @switchTo="switchView" />
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import HeaderComponent from '@/components/HeaderComponent.vue'
import LoginComponent from '@/components/LoginComponent.vue'
import RegisterComponent from '@/components/RegisterComponent.vue'
import ForgotPasswordComponent from '@/components/ForgotPasswordComponent.vue'

// Reactive data
const currentView = ref('login')
const showAuthModal = ref(false)

// Methods
const switchView = (view: string) => {
  currentView.value = view
  showAuthModal.value = false
}
</script>

<style scoped>
.landing-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #FFF8E1 0%, #FFFDE7 50%, #F1F8E9 100%);
}

.main-content {
  padding-top: 70px; /* 헤더 높이만큼 여백 */
}

.hero-section {
  min-height: calc(100vh - 70px);
  display: flex;
  align-items: center;
  background: linear-gradient(135deg, rgba(255, 248, 225, 0.9) 0%, rgba(255, 253, 231, 0.9) 50%, rgba(241, 248, 233, 0.9) 100%);
}

.hero-container {
  max-width: 1400px !important;
}

.min-height-screen {
  min-height: calc(100vh - 140px);
}

.hero-content {
  padding: 2rem 0;
}

.hero-title {
  font-size: 3.5rem !important;
  font-weight: 700;
  color: #333;
  line-height: 1.2;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
}

.hero-subtitle {
  font-size: 1.5rem;
  color: #666;
  font-weight: 400;
  margin-bottom: 2rem;
}

.hero-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.hero-btn {
  font-weight: 600 !important;
  text-transform: none !important;
  padding: 0 2rem !important;
  height: 56px !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transition: all 0.3s ease;
}

.hero-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
}

.auth-section {
  padding: 2rem 1rem;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 500px;
}

.inquiry-section {
  background: rgba(255, 255, 255, 0.7);
  padding: 4rem 0;
  backdrop-filter: blur(10px);
}

.inquiry-title {
  font-size: 2rem;
  font-weight: 600;
  color: #333;
}

.inquiry-content {
  max-width: 600px;
  margin: 0 auto;
}

.chat-icon {
  margin-top: 2rem;
  display: flex;
  justify-content: center;
}

/* 애니메이션 */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

/* 반응형 디자인 */
@media (max-width: 960px) {
  .hero-title {
    font-size: 2.5rem !important;
  }
  
  .hero-subtitle {
    font-size: 1.2rem;
  }
  
  .hero-buttons {
    flex-direction: column;
    align-items: center;
  }
  
  .hero-btn {
    width: 280px;
  }
  
  .auth-section {
    padding: 1rem;
    min-height: auto;
  }
}

@media (max-width: 600px) {
  .hero-title {
    font-size: 2rem !important;
  }
  
  .hero-content {
    padding: 1rem 0;
  }
}
</style>
