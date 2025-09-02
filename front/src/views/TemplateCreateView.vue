<template>
  <div class="template-create-page">
    <!-- 헤더 -->
    <HeaderComponent />
    
    <!-- 메인 콘텐츠 -->
    <v-main class="main-content">
      <v-container fluid class="pa-0">
        <section class="template-section">
          <v-container class="template-container">
            <v-row justify="center" align="center" class="min-height-screen">
              <v-col cols="12" md="8" lg="6" class="text-center">
                <div class="template-content">
                  <!-- 제목 -->
                  <h1 class="template-title mb-6">
                    카카오 알림톡으로 발송할 메시지 내용을 입력하세요
                  </h1>
                  
                  <!-- 부제목 -->
                  <p class="template-subtitle mb-8">
                    문자 메시지를 보낸다고 생각하시고 메시지를 입력해주세요
                  </p>
                  
                  <!-- 카테고리 선택 -->
                  <div class="category-section mb-8">
                    <h3 class="category-title mb-4">카테고리 선택</h3>
                    <div class="category-buttons">
                      <v-btn
                        v-for="category in categories"
                        :key="category.id"
                        :color="selectedCategory === category.id ? '#00C851' : '#E0E0E0'"
                        :variant="selectedCategory === category.id ? 'flat' : 'outlined'"
                        class="category-btn mr-4 mb-2"
                        rounded="pill"
                        size="large"
                        @click="selectCategory(category.id)"
                      >
                        {{ category.name }}
                      </v-btn>
                    </div>
                  </div>
                  
                  <!-- 메시지 입력 -->
                  <div class="message-section mb-8">
                    <h3 class="message-title mb-4">메시지 내용</h3>
                    <v-textarea
                      v-model="messageText"
                      placeholder="여기에 메시지 내용을 입력하세요..."
                      variant="outlined"
                      rows="8"
                      class="message-input"
                      :rules="messageRules"
                      counter
                      maxlength="500"
                      auto-grow
                    ></v-textarea>
                  </div>
                  
                  <!-- 제출 버튼 -->
                  <div class="submit-section">
                    <v-btn
                      color="#00C851"
                      variant="flat"
                      size="x-large"
                      class="submit-btn"
                      rounded="pill"
                      :disabled="!canSubmit"
                      @click="submitTemplate"
                    >
                      템플릿 생성하기
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
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import HeaderComponent from '@/components/HeaderComponent.vue'

const router = useRouter()

// 카테고리 데이터
const categories = [
  { id: 'appointment', name: '예약 안내' },
  { id: 'marketing', name: '마케팅' },
  { id: 'notification', name: '공지사항' },
  { id: 'reminder', name: '리마인더' },
  { id: 'custom', name: '커스텀' }
]

// Reactive data
const selectedCategory = ref('')
const messageText = ref('')

// 유효성 검사 규칙
const messageRules = [
  (v: string) => !!v || '메시지 내용을 입력해주세요',
  (v: string) => v.length >= 10 || '메시지는 최소 10자 이상 입력해주세요'
]

// 제출 가능 여부
const canSubmit = computed(() => {
  return selectedCategory.value && messageText.value.trim().length >= 10
})

// 카테고리 선택
const selectCategory = (categoryId: string) => {
  selectedCategory.value = categoryId
}

// 템플릿 제출
const submitTemplate = () => {
  if (!canSubmit.value) return
  
  // 채팅 페이지로 이동
  router.push({
    name: 'chat',
    query: {
      category: selectedCategory.value,
      message: messageText.value
    }
  })
}
</script>

<style scoped>
.template-create-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #FFF8E1 0%, #FFFDE7 50%, #F1F8E9 100%);
}

.main-content {
  padding-top: 70px; /* 헤더 높이만큼 여백 */
}

.template-section {
  min-height: calc(100vh - 70px);
  display: flex;
  align-items: center;
  background: linear-gradient(135deg, rgba(255, 248, 225, 0.9) 0%, rgba(255, 253, 231, 0.9) 50%, rgba(241, 248, 233, 0.9) 100%);
}

.template-container {
  max-width: 1200px !important;
}

.min-height-screen {
  min-height: calc(100vh - 140px);
}

.template-content {
  padding: 2rem 0;
}

.template-title {
  font-size: 2.5rem !important;
  font-weight: 700;
  color: #333;
  line-height: 1.3;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
}

.template-subtitle {
  font-size: 1.2rem;
  color: #666;
  font-weight: 400;
  line-height: 1.5;
}

.category-section, .message-section {
  background: rgba(255, 255, 255, 0.8);
  padding: 2rem;
  border-radius: 16px;
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.category-title, .message-title {
  font-size: 1.3rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 1rem;
}

.category-buttons {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 1rem;
}

.category-btn {
  font-weight: 500 !important;
  text-transform: none !important;
  min-width: 120px;
  transition: all 0.3s ease;
}

.category-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.message-input {
  background: rgba(255, 255, 255, 0.9);
  border-radius: 12px;
}

.message-input :deep(.v-field__outline) {
  border-color: #E0E0E0;
}

.message-input :deep(.v-field--focused .v-field__outline) {
  border-color: #00C851;
}

.submit-section {
  margin-top: 2rem;
}

.submit-btn {
  font-weight: 600 !important;
  text-transform: none !important;
  padding: 0 3rem !important;
  height: 56px !important;
  box-shadow: 0 4px 12px rgba(0, 200, 81, 0.3);
  transition: all 0.3s ease;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 200, 81, 0.4);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 반응형 디자인 */
@media (max-width: 960px) {
  .template-title {
    font-size: 2rem !important;
  }
  
  .template-subtitle {
    font-size: 1.1rem;
  }
  
  .category-section, .message-section {
    padding: 1.5rem;
  }
}

@media (max-width: 600px) {
  .template-title {
    font-size: 1.8rem !important;
  }
  
  .template-content {
    padding: 1rem 0;
  }
  
  .category-buttons {
    flex-direction: column;
    align-items: center;
  }
  
  .category-btn {
    width: 200px;
  }
}
</style>
