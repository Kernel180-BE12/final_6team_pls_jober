<template>
  <v-app-bar
    color="#FFE066"
    elevation="2"
    height="70"
    class="header-bar"
  >
    <v-container fluid class="d-flex align-center">
      <!-- 로고 -->
      <v-app-bar-title class="logo-text">
        Pls Jober
      </v-app-bar-title>

      <!-- 네비게이션 메뉴 -->
      <v-spacer></v-spacer>
      
      <div class="nav-menu d-flex align-center">
        <v-btn
          variant="text"
          class="nav-btn"
          color="#333"
        >
          
        </v-btn>
        
        <!-- 템플릿 만들기 버튼 -->
        <v-btn
          color="#00C851"
          variant="flat"
          class="template-btn ml-4"
          rounded="pill"
          size="large"
          @click="goToTemplateCreate"
        >

        </v-btn>
      </div>
    </v-container>
  </v-app-bar>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

// 템플릿 생성 페이지로 이동
const goToTemplateCreate = () => {
  router.push({ name: 'template-create' })
}
</script>

<style scoped>
.header-bar {
  background: linear-gradient(135deg, #FFE066 0%, #FFD700 100%);
}

.logo-text {
  font-size: 28px !important;
  font-weight: bold;
  color: #333 !important;
  font-family: 'Arial', sans-serif;
}

.nav-menu {
  gap: 8px;
}

.nav-btn {
  font-size: 14px !important;
  font-weight: 500;
  text-transform: none !important;
  padding: 0 16px;
}

.template-btn {
  font-weight: 600 !important;
  text-transform: none !important;
  box-shadow: 0 2px 8px rgba(0, 200, 81, 0.3);
  transition: all 0.3s ease;
}

.template-btn:hover {
  box-shadow: 0 4px 12px rgba(0, 200, 81, 0.4);
  transform: translateY(-1px);
}
</style>
