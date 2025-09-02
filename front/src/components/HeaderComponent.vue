<template>
  <v-app-bar app elevation="1" color="white">
    <v-container class="d-flex align-center justify-space-between pa-0">
      <!-- 로고 -->
      <div class="d-flex align-center">
        <v-icon size="32" color="primary" class="mr-2">mdi-robot</v-icon>
        <span class="text-h6 font-weight-bold text-primary">AI Template</span>
      </div>
      
      <!-- 템플릿 작성하기 버튼 -->
      <v-btn
        color="primary"
        variant="elevated"
        prepend-icon="mdi-plus"
        @click="goToTemplateCreate"
      >
        템플릿 작성하기
      </v-btn>
    </v-container>
  </v-app-bar>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const goToTemplateCreate = () => {
  router.push('/template/create')
}
</script>

<style scoped>
.v-app-bar {
  border-bottom: 1px solid #e0e0e0;
}
</style>
