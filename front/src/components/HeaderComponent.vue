<template>
  <header class="header">
    <div class="header-container">
      <!-- 로고 -->
      <div class="logo">
        <button @click="$router.push('/')">
          <span class="logo-text">AI Template</span>
          <div class="logo-icon">🤖</div>
        </button>
      </div>
      
      <!-- 액션 버튼들 -->
      <div class="action-buttons">
        <button class="btn-mypage" @click="goToMyPage">
          마이페이지
        </button>
        <button class="btn-template" @click="goToTemplateCreate">
          템플릿 작성하기
        </button>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const goToMyPage = () => {
  router.push('/mypage')
}

const goToTemplateCreate = () => {
  router.push('/template/create')
}
</script>

<style scoped>
.header {
  background: linear-gradient(135deg, #1976d2 0%, #8E24AA 100%);
  padding: 0.6vw 0;
  box-shadow: 0 0.2rem 0.6rem rgba(25, 118, 210, 0.3);
  position: relative;
  overflow: hidden;
}

.header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(45deg, rgba(255, 255, 255, 0.1) 0%, transparent 50%, rgba(255, 255, 255, 0.1) 100%);
  pointer-events: none;
}

.header-container {
  max-width: 60rem;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 1.2rem;
  position: relative;
  z-index: 1;
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.logo-icon {
  font-size: 2rem;
  filter: drop-shadow(0 0.1rem 0.2rem rgba(0, 0, 0, 0.1));
}

.logo-text {
  font-size: 1.5rem;
  font-weight: 700;
  color: #fff;
  text-shadow: 0 0.05rem 0.1rem rgba(0, 0, 0, 0.3);
}

.logo button {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
}

.action-buttons {
  display: flex;
  gap: 0.8rem;
  align-items: center;
}

.btn-mypage,
.btn-template {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.2) 0%, rgba(255, 255, 255, 0.1) 100%);
  border: 0.1rem solid rgba(255, 255, 255, 0.8);
  color: #fff;
  padding: 0.6rem 1.2rem;
  border-radius: 0.4rem;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(0.5rem);
  box-shadow: 0 0.1rem 0.4rem rgba(0, 0, 0, 0.1);
}

.btn-mypage:hover,
.btn-template:hover {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.3) 0%, rgba(255, 255, 255, 0.2) 100%);
  color: #fff;
  border-color: rgba(255, 255, 255, 1);
  transform: translateY(-0.1rem);
  box-shadow: 0 0.2rem 0.8rem rgba(0, 0, 0, 0.2);
}
</style>
