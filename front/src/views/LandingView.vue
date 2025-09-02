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
              <!-- 왼쪽 콘텐츠 -->
              <v-col cols="12" md="6" class="text-center">
                <div class="hero-content">
                  <h1 class="hero-title mb-4">
                    AI 메시징 플랫폼
                  </h1>
                  <p class="hero-subtitle mb-8">
                    스마트한 메시지 관리 솔루션
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
                      시작하기
                    </v-btn>
                    
                    <v-btn
                      color="#00C851"
                      variant="flat"
                      size="x-large"
                      class="hero-btn"
                      rounded="pill"
                      @click="currentView = 'login'"
                    >
                      로그인 →
                    </v-btn>
                  </div>
                </div>
              </v-col>
              
              <!-- 오른쪽 인증 폼 (동적으로 표시) -->
              <v-col cols="12" md="6" class="text-center" v-if="currentView">
                <div class="auth-section">
                  <transition name="slide-fade" mode="out-in">
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
      </v-container>
    </v-main>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import HeaderComponent from '@/components/HeaderComponent.vue'
import LoginComponent from '@/components/LoginComponent.vue'
import RegisterComponent from '@/components/RegisterComponent.vue'
import ForgotPasswordComponent from '@/components/ForgotPasswordComponent.vue'

// Reactive data
const currentView = ref('')

// Methods
const switchView = (view: string) => {
  currentView.value = view
}
</script>

<style scoped>
.landing-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #FFF8E1 0%, #FFFDE7 50%, #F1F8E9 100%);
}

.main-content {
  padding-top: 50px; /* 헤더 높이만큼 여백을 줄임 */
}

.hero-section {
  min-height: calc(100vh - 50px); /* 헤더 높이를 반영하여 조정 */
  display: flex;
  align-items: center;
  background: linear-gradient(135deg, rgba(255, 248, 225, 0.9) 0%, rgba(255, 253, 231, 0.9) 50%, rgba(241, 248, 233, 0.9) 100%);
}

.hero-container {
  max-width: 1400px !important;
}

.min-height-screen {
  min-height: calc(100vh - 120px); /* 전체 높이를 줄여서 스크롤 방지 */
}

.hero-content {
  padding: 1.5rem 0; /* 패딩을 줄여서 공간 절약 */
}

.hero-title {
  font-size: 3rem !important; /* 제목 크기를 약간 줄임 */
  font-weight: 700;
  color: #333;
  line-height: 1.2;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
}

.hero-subtitle {
  font-size: 1.3rem; /* 부제목 크기를 약간 줄임 */
  color: #666;
  font-weight: 400;
  margin-bottom: 1.5rem; /* 마진을 줄임 */
}

.hero-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
  margin-bottom: 1.5rem; /* 마진을 줄임 */
}

.hero-btn {
  font-weight: 600 !important;
  text-transform: none !important;
  padding: 0 2rem !important;
  height: 52px !important; /* 버튼 높이를 약간 줄임 */
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transition: all 0.3s ease;
}

.hero-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
}

.auth-section {
  padding: 1.5rem 1rem; /* 패딩을 줄여서 공간 절약 */
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 450px; /* 최소 높이를 줄임 */
  width: 100%; /* 전체 너비 사용 */
  max-width: none; /* 최대 너비 제한 제거 */
}

/* 슬라이드 애니메이션 */
.slide-fade-enter-active {
  transition: all 0.3s ease-out;
}

.slide-fade-leave-active {
  transition: all 0.3s ease-in;
}

.slide-fade-enter-from {
  transform: translateX(30px);
  opacity: 0;
}

.slide-fade-leave-to {
  transform: translateX(-30px);
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
