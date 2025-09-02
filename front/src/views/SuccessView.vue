<template>
  <div class="success-page">
    <!-- 헤더 -->
    <HeaderComponent />
    
    <!-- 메인 콘텐츠 -->
    <v-main class="main-content">
      <v-container fluid class="pa-0">
        <section class="success-section">
          <v-container class="success-container">
            <v-row justify="center" align="center" class="min-height-screen">
              <v-col cols="12" md="8" lg="6" class="text-center">
                <div class="success-content">
                  <!-- 성공 메시지 -->
                  <div class="success-message mb-8">
                    <h1 class="success-title mb-4">
                      메세지를 성공적으로
                    </h1>
                    <h1 class="success-title">
                      전송하였습니다.
                    </h1>
                  </div>
                  
                  <!-- 박수 이모티콘 -->
                  <div class="clap-emoji mb-8">
                    <span class="emoji">👏</span>
                    <span class="emoji">👏</span>
                    <span class="emoji">👏</span>
                  </div>
                  
                  <!-- 액션 버튼들 -->
                  <div class="action-buttons">
                    <v-btn
                      color="#E0E0E0"
                      variant="flat"
                      class="action-btn mr-4 mb-2"
                      rounded="pill"
                      size="large"
                      @click="goToTemplateCreate"
                    >
                      추가 템플릿 이용
                    </v-btn>
                    
                    <v-btn
                      color="#E0E0E0"
                      variant="flat"
                      class="action-btn"
                      rounded="pill"
                      size="large"
                      @click="goToHome"
                    >
                      HOME
                    </v-btn>
                  </div>
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
import { useRouter } from 'vue-router'
import HeaderComponent from '@/components/HeaderComponent.vue'

const router = useRouter()

// 추가 템플릿 이용
const goToTemplateCreate = () => {
  router.push({ name: 'template-create' })
}

// 홈으로 이동
const goToHome = () => {
  router.push({ name: 'landing' })
}
</script>

<style scoped>
.success-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #FFF8E1 0%, #FFFDE7 50%, #F1F8E9 100%);
}

.main-content {
  padding-top: 70px; /* 헤더 높이만큼 여백 */
}

.success-section {
  min-height: calc(100vh - 70px);
  display: flex;
  align-items: center;
  background: linear-gradient(135deg, rgba(255, 248, 225, 0.9) 0%, rgba(255, 253, 231, 0.9) 50%, rgba(241, 248, 233, 0.9) 100%);
}

.success-container {
  max-width: 1200px !important;
}

.min-height-screen {
  min-height: calc(100vh - 140px);
}

.success-content {
  padding: 2rem 0;
}

.success-message {
  margin-bottom: 3rem;
}

.success-title {
  font-size: 3rem !important;
  font-weight: 700;
  color: #333;
  line-height: 1.2;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
  margin: 0;
}

.clap-emoji {
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin-bottom: 3rem;
}

.emoji {
  font-size: 4rem;
  animation: clap 1s ease-in-out infinite;
}

.emoji:nth-child(1) { animation-delay: 0s; }
.emoji:nth-child(2) { animation-delay: 0.2s; }
.emoji:nth-child(3) { animation-delay: 0.4s; }

@keyframes clap {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.2);
  }
}

.action-buttons {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.action-btn {
  background: #E0E0E0 !important;
  color: #333 !important;
  font-weight: 600 !important;
  text-transform: none !important;
  padding: 0 2rem !important;
  height: 56px !important;
  min-width: 180px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
  background: #D0D0D0 !important;
}

/* 반응형 디자인 */
@media (max-width: 960px) {
  .success-title {
    font-size: 2.5rem !important;
  }
  
  .emoji {
    font-size: 3.5rem;
  }
  
  .action-buttons {
    flex-direction: column;
    align-items: center;
  }
  
  .action-btn {
    width: 250px;
  }
}

@media (max-width: 600px) {
  .success-title {
    font-size: 2rem !important;
  }
  
  .emoji {
    font-size: 3rem;
  }
  
  .success-content {
    padding: 1rem 0;
  }
  
  .action-btn {
    width: 280px;
  }
}
</style>
