<script setup lang="ts">
  import "../assets/styles/btn.css"

  import { useUserStore } from '@/stores/user' // Pinia/Vuex 스토어 import
  import { useRoute } from "vue-router"
  import { computed } from "vue"

  const headerMenu = [
    { id: 1, text: "마이페이지", path: "/mypage" },
    { id: 2, text: "로그아웃", action: "logout" }
  ]

  const userStore = useUserStore()
  const route = useRoute()

  // 로그아웃 함수
  const handleLogout = () => {
    userStore.logout()
  }

  // 버튼 클릭 핸들러
  const handleMenuClick = (item: any) => {
    if (item.action === 'logout') {
      handleLogout()
    }
  }

  // 로그인, 마이페이지 진입 시 헤더 버튼 핸들링
  const visibleMenu = computed(() => {
    // 1번 버튼 = 마이페이지
    // 2번 버튼 = 로그아웃

    // 비 로그인 유저 = null
    if(!userStore.isLoggedIn)
      return null

    // 마이페이지 진입 = 로그아웃만 표시
    else if(route.path.startsWith("/mypage"))
      return headerMenu.filter(item => item.id === 2)

    // 랜딩 페이지 = 모든 버튼 표시
    else
      return headerMenu
  })
</script>

<template>
  <header class="header">
    <div class="header-container">
      <!-- 로고 -->
      <router-link to="/" class="logo">
        <div class="logo-icon">🤖</div>
        <span class="logo-text">AI Template</span>
      </router-link>

      <div class="header_menu">
        <template v-for="item in visibleMenu" :key="item.id">
          <router-link
            v-if="item.path"
            :to="item.path"
            class="btn btn-gradation"
            tabindex="0"
          >
            {{ item.text }}
          </router-link>
          <button
            v-else-if="item.action"
            @click="handleMenuClick(item)"
            class="btn btn-gradation"
            tabindex="0"
          >
            {{ item.text }}
          </button>
        </template>
      </div>
    </div>
  </header>
</template>

<style scoped>
.header {
  background: linear-gradient(135deg, #1976d2 0%, #8E24AA 100%);
  padding: 0.6vw 0;
  box-shadow: 0 0.2rem 0.6rem rgba(25, 118, 210, 0.3);
  position: relative;
  overflow: hidden;
  width: 100%;
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

.header a{
  text-decoration: none;
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

.header_menu{
  display: flex;
  gap: 10px;
}
</style>
