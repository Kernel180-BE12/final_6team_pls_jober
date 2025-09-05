<template>
  <div class="success-container">
    <!-- 헤더 컴포넌트 -->
    <HeaderComponent />
    
    <!-- 메인 콘텐츠 -->
    <main class="main-content">
      <div class="content-wrapper">
        <div class="success-section">
          <h1 class="success-title">메세지를 성공적으로 전송하였습니다.</h1>
          
          <div class="celebration-emoji">
            <span class="emoji">👏</span>
            <span class="emoji">👏</span>
            <span class="emoji">👏</span>
          </div>
          
          <div class="action-buttons">
            <button class="btn-additional">추가 템플릿 이용</button>
            <button class="btn-home" @click="goHome">HOME</button>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import HeaderComponent from '@/components/HeaderComponent.vue'

const router = useRouter()

const goHome = () => {
  router.push('/')
}
</script>

<style scoped>
.success-container {
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
  padding: 4rem 0;
}

.content-wrapper {
  max-width: 800px;
  margin: 0 auto;
  text-align: center;
  padding: 0 1.2rem;
}

.success-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2rem;
}

.success-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #333;
  margin: 0;
  line-height: 1.3;
}

.celebration-emoji {
  display: flex;
  gap: 0.8rem;
}

.emoji {
  font-size: 3rem;
}

.action-buttons {
  display: flex;
  gap: 1.2rem;
  margin-top: 0.8rem;
}

.btn-additional,
.btn-home {
  background-color: #6c757d;
  color: white;
  border: none;
  padding: 0.8rem 1.6rem;
  border-radius: 0.4rem;
  font-weight: 600;
  font-size: 1.1rem;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.btn-additional:hover,
.btn-home:hover {
  background-color: #5a6268;
}
</style>
