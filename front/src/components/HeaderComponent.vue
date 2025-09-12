<script setup lang="ts">
  import "../assets/styles/btn.css"

  const headerMenu = [
    { id: 1, text: "마이페이지", path: "/mypage" },
    { id: 2, text: "템플릿 작성하기", path: "/template/create" }
  ]
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
      <!-- 액션 버튼들 -->
        <router-link
            v-for="item in headerMenu"
            :key="item.id"
            :to="item.path"
            class="btn btn-gradation"
        >
          {{ item.text }}
        </router-link>
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
